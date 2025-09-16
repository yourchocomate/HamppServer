"""Server management functionality for HamppServer."""

import os
import subprocess
import time
import psutil
import requests
from pathlib import Path
from typing import Optional, Dict
from dataclasses import dataclass

from hampp.core.config import Config
from hampp.utils.logger import setup_logger
from hampp.utils.file_ops import write_file, backup_file, read_file
from hampp.utils.validators import validate_port

logger = setup_logger(__name__)


@dataclass
class ServiceStatus:
    """Status information for a service."""
    
    name: str
    running: bool
    pid: Optional[int] = None
    port: Optional[int] = None
    uptime: Optional[float] = None
    memory_usage: Optional[float] = None
    cpu_usage: Optional[float] = None


class ServerManager:
    """Manages Apache, MySQL, and PHP services."""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize server manager.
        
        Args:
            config: Configuration instance
        """
        self.config = config or Config()
        self.logger = setup_logger(__name__)
        
        # Service configurations
        self.services = {
            'apache': {
                'name': 'Apache HTTP Server',
                'binary': self.config.path_config.apache_bin,
                'config_file': self.config.path_config.apache_config,
                'pid_file': f"{self.config.path_config.pid_dir}/apache2/httpd.pid",
                'port': self.config.server_config.apache_port,
            },
            'mysql': {
                'name': 'MySQL/MariaDB Server',
                'binary': self.config.path_config.mysql_bin,
                'config_file': self.config.path_config.mysql_config,
                'pid_file': f"{self.config.path_config.pid_dir}/mysqld.pid",
                'port': self.config.server_config.mysql_port,
            }
        }
    
    def start_apache(self, port: Optional[int] = None, 
                    document_root: Optional[str] = None) -> bool:
        """Start Apache server.
        
        Args:
            port: Optional custom port
            document_root: Optional custom document root
        
        Returns:
            True if Apache started successfully
        """
        try:
            # Validate inputs
            if port:
                valid, port_int, error = validate_port(str(port))
                if not valid:
                    logger.error(f"Invalid port: {error}")
                    return False
                port = port_int
            else:
                port = self.config.server_config.apache_port
            
            if document_root:
                from hampp.utils.validators import validate_directory
                valid, error = validate_directory(document_root)
                if not valid:
                    logger.error(f"Invalid document root: {error}")
                    return False
            else:
                document_root = self.config.server_config.document_root
            
            # Check if already running
            if self.is_service_running('apache'):
                logger.info("Apache is already running")
                return True
            
            # Setup Apache configuration
            if not self._setup_apache_config(port, document_root):
                logger.error("Failed to setup Apache configuration")
                return False
            
            # Start Apache
            cmd = [self.services['apache']['binary'], 'start']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                logger.error(f"Failed to start Apache: {result.stderr}")
                return False
            
            # Verify Apache is running
            time.sleep(2)  # Give Apache time to start
            
            if not self._verify_apache_running(port):
                logger.error("Apache failed to start properly")
                return False
            
            logger.info(f"Apache started successfully on port {port}")
            logger.info(f"Document root: {document_root}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error starting Apache: {e}")
            return False
    
    def stop_apache(self) -> bool:
        """Stop Apache server.
        
        Returns:
            True if Apache stopped successfully
        """
        try:
            # Check if running
            if not self.is_service_running('apache'):
                logger.info("Apache is not running")
                return True
            
            # Stop Apache
            cmd = [self.services['apache']['binary'], 'stop']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            # Also try to kill process if stop command fails
            if result.returncode != 0:
                logger.warning(f"Apache stop command failed: {result.stderr}")
                logger.info("Attempting to kill Apache processes")
                
                # Kill httpd processes
                try:
                    subprocess.run(['killall', 'httpd'], capture_output=True, timeout=10)
                    subprocess.run(['pkill', '-f', 'apache'], capture_output=True, timeout=10)
                except Exception:
                    pass
            
            # Remove PID file if it exists
            pid_file = Path(self.services['apache']['pid_file'])
            if pid_file.exists():
                try:
                    pid_file.unlink()
                except Exception as e:
                    logger.debug(f"Could not remove PID file: {e}")
            
            # Verify Apache is stopped
            time.sleep(1)
            
            if self.is_service_running('apache'):
                logger.error("Failed to stop Apache")
                return False
            
            logger.info("Apache stopped successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping Apache: {e}")
            return False
    
    def start_mysql(self) -> bool:
        """Start MySQL/MariaDB server.
        
        Returns:
            True if MySQL started successfully
        """
        try:
            # Check if already running
            if self.is_service_running('mysql'):
                logger.info("MySQL is already running")
                return True
            
            # Start MySQL based on platform and available binaries
            if self.config.platform.is_termux:
                # Try different Termux MySQL/MariaDB startup methods
                prefix = "/data/data/com.termux/files/usr"
                
                # Method 1: Try mariadbd directly
                if os.path.exists(f"{prefix}/bin/mariadbd"):
                    cmd = [f"{prefix}/bin/mariadbd", "--user=mysql", "--daemonize"]
                # Method 2: Try mysqld_safe
                elif os.path.exists(f"{prefix}/bin/mysqld_safe"):
                    cmd = [f"{prefix}/bin/mysqld_safe", "--user=mysql", "--datadir=/data/data/com.termux/files/usr/var/lib/mysql", "&"]
                # Method 3: Try mysqld directly
                elif os.path.exists(f"{prefix}/bin/mysqld"):
                    cmd = [f"{prefix}/bin/mysqld", "--user=mysql", "--daemonize"]
                else:
                    logger.error("No MySQL/MariaDB binary found in Termux")
                    return False
            else:
                # Linux/other systems
                if os.path.exists('/usr/bin/mysqld'):
                    cmd = ['mysqld', '--daemonize']
                elif os.path.exists('/usr/sbin/mysqld'):
                    cmd = ['/usr/sbin/mysqld', '--daemonize']
                else:
                    cmd = ['mysqld', '--daemonize']
            
            # Ensure MySQL data directory exists
            if self.config.platform.is_termux:
                mysql_data_dir = "/data/data/com.termux/files/usr/var/lib/mysql"
            else:
                mysql_data_dir = "/var/lib/mysql"
            
            if not os.path.exists(mysql_data_dir):
                logger.info("Initializing MySQL data directory...")
                if self.config.platform.is_termux:
                    init_cmd = [f"{prefix}/bin/mysql_install_db", "--user=mysql", f"--datadir={mysql_data_dir}"]
                else:
                    init_cmd = ["mysql_install_db", "--user=mysql", f"--datadir={mysql_data_dir}"]
                
                init_result = subprocess.run(init_cmd, capture_output=True, text=True, timeout=60)
                if init_result.returncode != 0:
                    logger.warning(f"MySQL init warning: {init_result.stderr}")
            
            # Start MySQL
            logger.info(f"Starting MySQL with command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                logger.error(f"Failed to start MySQL: {result.stderr}")
                logger.info(f"Trying alternative startup method...")
                
                # Try alternative method for Termux
                if self.config.platform.is_termux:
                    alt_cmd = [f"{prefix}/bin/mysqld_safe", "--user=mysql"]
                    result = subprocess.run(alt_cmd, capture_output=True, text=True, timeout=10)
                    if result.returncode != 0:
                        logger.error(f"Alternative MySQL start also failed: {result.stderr}")
                        return False
            
            # Verify MySQL is running
            time.sleep(3)  # Give MySQL time to start
            
            if not self.is_service_running('mysql'):
                logger.error("MySQL failed to start properly")
                return False
            
            logger.info(f"MySQL started successfully on port {self.services['mysql']['port']}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error starting MySQL: {e}")
            return False
    
    def stop_mysql(self) -> bool:
        """Stop MySQL/MariaDB server.
        
        Returns:
            True if MySQL stopped successfully
        """
        try:
            # Check if running
            if not self.is_service_running('mysql'):
                logger.info("MySQL is not running")
                return True
            
            # Stop MySQL
            if self.config.platform.is_termux:
                cmd = [self.services['mysql']['binary'], 'stop']
            else:
                cmd = ['mysqladmin', 'shutdown']
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            # Also try to kill process if stop command fails
            if result.returncode != 0:
                logger.warning(f"MySQL stop command failed: {result.stderr}")
                logger.info("Attempting to kill MySQL processes")
                
                try:
                    subprocess.run(['killall', 'mysqld'], capture_output=True, timeout=10)
                    subprocess.run(['pkill', '-f', 'mysql'], capture_output=True, timeout=10)
                except Exception:
                    pass
            
            # Verify MySQL is stopped
            time.sleep(1)
            
            if self.is_service_running('mysql'):
                logger.error("Failed to stop MySQL")
                return False
            
            logger.info("MySQL stopped successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping MySQL: {e}")
            return False
    
    def restart_service(self, service: str) -> bool:
        """Restart a service.
        
        Args:
            service: Service name ('apache' or 'mysql')
        
        Returns:
            True if service restarted successfully
        """
        if service == 'apache':
            return self.stop_apache() and self.start_apache()
        elif service == 'mysql':
            return self.stop_mysql() and self.start_mysql()
        else:
            logger.error(f"Unknown service: {service}")
            return False
    
    def get_service_status(self, service: str) -> ServiceStatus:
        """Get status of a service.
        
        Args:
            service: Service name ('apache' or 'mysql')
        
        Returns:
            ServiceStatus object
        """
        service_config = self.services.get(service)
        if not service_config:
            return ServiceStatus(name=service, running=False)
        
        running = self.is_service_running(service)
        pid = self._get_service_pid(service) if running else None
        
        status = ServiceStatus(
            name=service_config['name'],
            running=running,
            pid=pid,
            port=service_config['port']
        )
        
        # Get process information if running
        if pid:
            try:
                process = psutil.Process(pid)
                status.uptime = time.time() - process.create_time()
                status.memory_usage = process.memory_info().rss / 1024 / 1024  # MB
                status.cpu_usage = process.cpu_percent()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        return status
    
    def get_all_status(self) -> Dict[str, ServiceStatus]:
        """Get status of all services.
        
        Returns:
            Dictionary mapping service names to ServiceStatus objects
        """
        return {
            service: self.get_service_status(service)
            for service in self.services.keys()
        }
    
    def is_service_running(self, service: str) -> bool:
        """Check if a service is running.
        
        Args:
            service: Service name ('apache' or 'mysql')
        
        Returns:
            True if service is running
        """
        # Check by PID file
        pid = self._get_service_pid(service)
        if pid and self._is_process_running(pid):
            return True
        
        # Check by port
        port = self.services[service]['port']
        if self._is_port_in_use(port):
            return True
        
        # Check by process name
        process_names = {
            'apache': ['httpd', 'apache2'],
            'mysql': ['mysqld', 'mariadb']
        }
        
        if service in process_names:
            for proc_name in process_names[service]:
                if self._is_process_running_by_name(proc_name):
                    return True
        
        return False
    
    def _setup_apache_config(self, port: int, document_root: str) -> bool:
        """Setup Apache configuration.
        
        Args:
            port: Apache port
            document_root: Document root directory
        
        Returns:
            True if configuration was setup successfully
        """
        try:
            config_file = self.services['apache']['config_file']
            
            # Backup original config
            if not backup_file(config_file):
                logger.warning("Could not backup Apache configuration")
            
            # Generate configuration
            config_content = self._generate_apache_config(port, document_root)
            
            # Write configuration
            if not write_file(config_file, config_content):
                logger.error("Failed to write Apache configuration")
                return False
            
            logger.debug("Apache configuration updated")
            return True
            
        except Exception as e:
            logger.error(f"Error setting up Apache configuration: {e}")
            return False
    
    def _generate_apache_config(self, port: int, document_root: str) -> str:
        """Generate Apache configuration content.
        
        Args:
            port: Apache port
            document_root: Document root directory
        
        Returns:
            Apache configuration content
        """
        # This is a simplified config - in a real implementation,
        # you'd want to use Jinja2 templates
        
        php_module = self._detect_php_module()
        
        if self.config.platform.is_termux:
            # Termux-specific configuration
            prefix = "/data/data/com.termux/files/usr"
            modules_dir = f"{prefix}/lib/apache2/modules"
            
            config = f"""
# HamppServer Apache Configuration for Termux
# Generated automatically - do not edit manually

ServerRoot "{prefix}"
Listen {port}

# PHP Module
{php_module}

# Basic modules
LoadModule mpm_prefork_module {modules_dir}/mod_mpm_prefork.so
LoadModule authz_core_module {modules_dir}/mod_authz_core.so
LoadModule dir_module {modules_dir}/mod_dir.so
LoadModule mime_module {modules_dir}/mod_mime.so

# Server identification
ServerName localhost
ServerAdmin admin@localhost

# Document root
DocumentRoot "{document_root}"

# Directory permissions
<Directory "{document_root}">
    Options Indexes FollowSymLinks
    AllowOverride All
    Require all granted
</Directory>

# Directory index
DirectoryIndex index.html index.htm index.php

# PHP file handling
<FilesMatch \\.php$>
    SetHandler application/x-httpd-php
</FilesMatch>

# MIME types
TypesConfig {prefix}/etc/apache2/mime.types

# Error and access logs
ErrorLog {prefix}/var/log/apache2/error.log
CustomLog {prefix}/var/log/apache2/access.log combined

# Process ID file
PidFile {prefix}/var/run/apache2/httpd.pid
"""
        else:
            # Linux/other systems configuration
            config = f"""
# HamppServer Apache Configuration
# Generated automatically - do not edit manually

ServerRoot "{self.config.path_config.apache_config.rsplit('/', 2)[0]}"
Listen {port}

# PHP Module
{php_module}

# Basic modules
LoadModule mpm_prefork_module libexec/apache2/mod_mpm_prefork.so
LoadModule authz_core_module libexec/apache2/mod_authz_core.so
LoadModule dir_module libexec/apache2/mod_dir.so
LoadModule mime_module libexec/apache2/mod_mime.so

# Server identification
ServerName localhost
ServerAdmin admin@localhost

# Document root
DocumentRoot "{document_root}"

# Directory permissions
<Directory "{document_root}">
    Options Indexes FollowSymLinks
    AllowOverride All
    Require all granted
</Directory>

# Directory index
DirectoryIndex index.html index.htm index.php

# PHP file handling
<FilesMatch \\.php$>
    SetHandler application/x-httpd-php
</FilesMatch>

# MIME types
TypesConfig {self.config.path_config.apache_config.rsplit('/', 1)[0]}/mime.types

# Error and access logs
ErrorLog {self.config.path_config.log_dir}/apache2/error.log
CustomLog {self.config.path_config.log_dir}/apache2/access.log combined

# Process ID file
PidFile {self.services['apache']['pid_file']}
"""
        
        return config
    
    def _detect_php_module(self) -> str:
        """Detect PHP module configuration.
        
        Returns:
            PHP module configuration lines
        """
        if self.config.platform.is_termux:
            # Termux-specific PHP module detection
            prefix = "/data/data/com.termux/files/usr"
            php_modules = [
                (f"{prefix}/lib/apache2/modules/libphp.so", "php"),
                (f"{prefix}/libexec/apache2/libphp.so", "php"),
                (f"{prefix}/lib/apache2/modules/libphp8.so", "php8"),
                (f"{prefix}/lib/apache2/modules/libphp7.so", "php7"),
            ]
            
            for module_path, module_name in php_modules:
                if os.path.exists(module_path):
                    return f"LoadModule {module_name}_module {module_path}"
            
            # Termux fallback - check if PHP-Apache package is installed
            return f"LoadModule php_module {prefix}/lib/apache2/modules/libphp.so"
        else:
            # Non-Termux systems
            php_modules = [
                ('libphp.so', 'php'),
                ('libphp8.so', 'php8'),
                ('libphp7.so', 'php7'),
            ]
            
            module_dir = f"{self.config.path_config.apache_config.rsplit('/', 2)[0]}/libexec/apache2"
            
            for module_file, module_name in php_modules:
                module_path = f"{module_dir}/{module_file}"
                if os.path.exists(module_path):
                    return f"LoadModule {module_name}_module {module_path}"
            
            # Default fallback
            return "LoadModule php_module libexec/apache2/libphp.so"
    
    def _verify_apache_running(self, port: int) -> bool:
        """Verify Apache is running by making HTTP request.
        
        Args:
            port: Apache port to check
        
        Returns:
            True if Apache is responding
        """
        try:
            url = f"http://127.0.0.1:{port}"
            response = requests.get(url, timeout=5)
            
            # Check if response indicates Apache
            server_header = response.headers.get('server', '').lower()
            return 'apache' in server_header or response.status_code < 500
            
        except requests.RequestException:
            return False
    
    def _get_service_pid(self, service: str) -> Optional[int]:
        """Get PID of a service from PID file.
        
        Args:
            service: Service name
        
        Returns:
            PID if found, None otherwise
        """
        try:
            pid_file = Path(self.services[service]['pid_file'])
            if pid_file.exists():
                pid_content = read_file(pid_file)
                if pid_content:
                    return int(pid_content.strip())
        except (ValueError, FileNotFoundError):
            pass
        
        return None
    
    def _is_process_running(self, pid: int) -> bool:
        """Check if process with given PID is running.
        
        Args:
            pid: Process ID
        
        Returns:
            True if process is running
        """
        try:
            return psutil.pid_exists(pid)
        except Exception:
            return False
    
    def _is_process_running_by_name(self, name: str) -> bool:
        """Check if process with given name is running.
        
        Args:
            name: Process name
        
        Returns:
            True if process is running
        """
        try:
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] == name:
                    return True
        except Exception:
            pass
        
        return False
    
    def _is_port_in_use(self, port: int) -> bool:
        """Check if port is in use.
        
        Args:
            port: Port number to check
        
        Returns:
            True if port is in use
        """
        try:
            connections = psutil.net_connections()
            for conn in connections:
                if conn.laddr.port == port and conn.status == psutil.CONN_LISTEN:
                    return True
        except Exception:
            pass
        
        return False
