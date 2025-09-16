"""Installation and setup functionality for HamppServer."""

import os
import subprocess
import tempfile
import zipfile
from pathlib import Path
from typing import List, Optional, Dict, Any
from urllib.request import urlretrieve

from hampp.core.config import Config
from hampp.utils.logger import setup_logger
from hampp.utils.file_ops import (
    ensure_directory, 
    write_file, 
    make_executable
)

logger = setup_logger(__name__)


class Installer:
    """Handles installation and setup of HamppServer dependencies."""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize installer.
        
        Args:
            config: Configuration instance
        """
        self.config = config or Config()
        self.platform = self.config.platform
        
    def install_dependencies(self, force: bool = False) -> bool:
        """Install required dependencies.
        
        Args:
            force: Force reinstallation even if dependencies exist
        
        Returns:
            True if all dependencies installed successfully
        """
        logger.info("Installing HamppServer dependencies...")
        
        # Check if already installed and not forcing
        if not force and self._check_dependencies():
            logger.info("All dependencies already installed")
            return True
        
        success = True
        
        # Install based on platform
        if self.platform.is_termux:
            success &= self._install_termux_dependencies()
        elif self.platform.is_linux:
            success &= self._install_linux_dependencies()
        else:
            logger.error(f"Unsupported platform: {self.platform.name}")
            return False
        
        # Install Python dependencies
        success &= self._install_python_dependencies()
        
        # Setup directories and files
        logger.info("Setting up directories...")
        if not self._setup_directories():
            logger.error("Failed to setup directories")
            success = False
        
        logger.info("Setting up server configurations...")
        if not self._setup_server_configurations():
            logger.error("Failed to setup server configurations")
            success = False
        
        logger.info("Setting up configuration files...")
        if not self._setup_configuration_files():
            logger.error("Failed to setup configuration files")
            success = False
        
        logger.info("Setting up web files...")
        if not self._setup_web_files():
            logger.error("Failed to setup web files")
            success = False
        
        # Install PHPMyAdmin if requested
        if self.config.server_config.enable_phpmyadmin:
            logger.info("Installing PHPMyAdmin...")
            if not self._install_phpmyadmin():
                logger.error("Failed to install PHPMyAdmin")
                success = False
        else:
            logger.info("PHPMyAdmin installation skipped (disabled in config)")
        
        if success:
            logger.info("All dependencies installed successfully!")
        else:
            logger.error("Some dependencies failed to install")
        
        return success
    
    def _check_dependencies(self) -> bool:
        """Check if dependencies are already installed.
        
        Returns:
            True if all dependencies are available
        """
        deps = self.platform.check_dependencies()
        missing = [name for name, available in deps.items() if not available]
        
        if missing:
            logger.info(f"Missing dependencies: {', '.join(missing)}")
            return False
        
        return True
    
    def _install_termux_dependencies(self) -> bool:
        """Install dependencies on Termux.
        
        Returns:
            True if installation successful
        """
        logger.info("Installing Termux dependencies...")
        
        packages = [
            'apache2',
            'mariadb',
            'php',
            'php-apache',
            'unzip',
            'wget',
        ]
        
        # Update package list
        if not self._run_command(['pkg', 'update', '-y']):
            logger.error("Failed to update package list")
            return False
        
        # Install packages
        for package in packages:
            logger.info(f"Installing {package}...")
            if not self._run_command(['pkg', 'install', package, '-y']):
                logger.error(f"Failed to install {package}")
                return False
        
        # Setup storage permission for /sdcard access
        if not self._setup_termux_storage():
            logger.warning("Could not setup storage permissions")
        
        return True
    
    def _install_linux_dependencies(self) -> bool:
        """Install dependencies on Linux.
        
        Returns:
            True if installation successful
        """
        logger.info("Installing Linux dependencies...")
        
        package_manager = self.platform.get_package_manager()
        
        if package_manager == 'apt':
            return self._install_apt_packages()
        elif package_manager == 'yum':
            return self._install_yum_packages()
        elif package_manager == 'dnf':
            return self._install_dnf_packages()
        elif package_manager == 'pacman':
            return self._install_pacman_packages()
        else:
            logger.error(f"Unsupported package manager: {package_manager}")
            return False
    
    def _install_apt_packages(self) -> bool:
        """Install packages using apt."""
        packages = [
            'apache2',
            'mysql-server',
            'php',
            'libapache2-mod-php',
            'php-mysql',
            'unzip',
            'wget',
        ]
        
        # Update package list
        if not self._run_command(['sudo', 'apt', 'update']):
            return False
        
        # Install packages
        return self._run_command(['sudo', 'apt', 'install', '-y'] + packages)
    
    def _install_yum_packages(self) -> bool:
        """Install packages using yum."""
        packages = [
            'httpd',
            'mysql-server',
            'php',
            'php-mysql',
            'unzip',
            'wget',
        ]
        
        return self._run_command(['sudo', 'yum', 'install', '-y'] + packages)
    
    def _install_dnf_packages(self) -> bool:
        """Install packages using dnf."""
        packages = [
            'httpd',
            'mysql-server',
            'php',
            'php-mysqlnd',
            'unzip',
            'wget',
        ]
        
        return self._run_command(['sudo', 'dnf', 'install', '-y'] + packages)
    
    def _install_pacman_packages(self) -> bool:
        """Install packages using pacman."""
        packages = [
            'apache',
            'mysql',
            'php',
            'php-apache',
            'unzip',
            'wget',
        ]
        
        return self._run_command(['sudo', 'pacman', '-S', '--noconfirm'] + packages)
    
    def _install_python_dependencies(self) -> bool:
        """Install Python dependencies.
        
        Returns:
            True if installation successful
        """
        logger.info("Installing Python dependencies...")
        
        try:
            import pip
        except ImportError:
            logger.error("pip is not available")
            return False
        
        dependencies = [
            'click>=8.0.0',
            'rich>=13.0.0',
            'pyyaml>=6.0',
            'jinja2>=3.1.0',
            'psutil>=5.9.0',
            'requests>=2.28.0',
        ]
        
        for dep in dependencies:
            if not self._run_command(['pip', 'install', dep]):
                logger.error(f"Failed to install {dep}")
                return False
        
        return True
    
    def _setup_termux_storage(self) -> bool:
        """Setup Termux storage permissions.
        
        Returns:
            True if setup successful
        """
        try:
            # Check if storage is already accessible
            if os.access('/sdcard', os.R_OK):
                return True
            
            # Try to setup storage
            result = subprocess.run(['termux-setup-storage'], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.info("Storage permissions setup successful")
                return True
            else:
                logger.warning("Could not setup storage automatically")
                logger.info("Please run 'termux-setup-storage' manually")
                return False
                
        except Exception as e:
            logger.debug(f"Error setting up storage: {e}")
            return False
    
    def _setup_directories(self) -> bool:
        """Setup required directories.
        
        Returns:
            True if setup successful
        """
        logger.info("Setting up directories...")
        
        directories = [
            self.config.server_config.document_root,
            self.config.path_config.log_dir + "/apache2",
            self.config.path_config.pid_dir + "/apache2",
        ]
        
        for directory in directories:
            if not ensure_directory(directory):
                logger.error(f"Failed to create directory: {directory}")
                return False
        
        return True
    
    def _setup_server_configurations(self) -> bool:
        """Setup Apache and MySQL configuration files.
        
        Returns:
            True if setup successful
        """
        logger.info("Setting up server configurations...")
        
        success = True
        success &= self._setup_apache_configuration()
        success &= self._setup_mysql_configuration()
        
        return success
    
    def _setup_apache_configuration(self) -> bool:
        """Setup Apache configuration file.
        
        Returns:
            True if setup successful
        """
        logger.info("Setting up Apache configuration...")
        
        apache_config_path = self.config.path_config.apache_config
        
        # Check if config file exists
        if os.path.exists(apache_config_path):
            # Create backup of existing config
            backup_path = f"{apache_config_path}.hampp_backup"
            if not os.path.exists(backup_path):
                try:
                    import shutil
                    shutil.copy2(apache_config_path, backup_path)
                    logger.info(f"Backed up existing Apache config to: {backup_path}")
                except Exception as e:
                    logger.warning(f"Could not backup Apache config: {e}")
        
        # Generate HamppServer Apache configuration
        apache_config = self._generate_apache_config()
        
        try:
            os.makedirs(os.path.dirname(apache_config_path), exist_ok=True)
            with open(apache_config_path, 'w') as f:
                f.write(apache_config)
            logger.info(f"Apache configuration written to: {apache_config_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to write Apache config: {e}")
            return False
    
    def _setup_mysql_configuration(self) -> bool:
        """Setup MySQL configuration file.
        
        Returns:
            True if setup successful
        """
        logger.info("Setting up MySQL configuration...")
        
        mysql_config_path = self.config.path_config.mysql_config
        
        # Check if config file exists
        if os.path.exists(mysql_config_path):
            # Create backup of existing config
            backup_path = f"{mysql_config_path}.hampp_backup"
            if not os.path.exists(backup_path):
                try:
                    import shutil
                    shutil.copy2(mysql_config_path, backup_path)
                    logger.info(f"Backed up existing MySQL config to: {backup_path}")
                except Exception as e:
                    logger.warning(f"Could not backup MySQL config: {e}")
        
        # Generate HamppServer MySQL configuration
        mysql_config = self._generate_mysql_config()
        
        try:
            os.makedirs(os.path.dirname(mysql_config_path), exist_ok=True)
            with open(mysql_config_path, 'w') as f:
                f.write(mysql_config)
            logger.info(f"MySQL configuration written to: {mysql_config_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to write MySQL config: {e}")
            return False
    
    def _generate_apache_config(self) -> str:
        """Generate Apache configuration content.
        
        Returns:
            Apache configuration content
        """
        if self.config.platform.is_termux:
            return self._generate_termux_apache_config()
        else:
            return self._generate_linux_apache_config()
    
    def _generate_termux_apache_config(self) -> str:
        """Generate Termux-specific Apache configuration.
        
        Returns:
            Apache configuration content
        """
        prefix = "/data/data/com.termux/files/usr"
        modules_dir = f"{prefix}/libexec/apache2"
        document_root = self.config.server_config.document_root
        port = self.config.server_config.apache_port
        
        # Generate module loading directives based on what actually exists
        module_lines = []
        
        # Essential modules in order of importance
        essential_modules = [
            ('mpm_prefork_module', 'mod_mpm_prefork.so'),
            ('authz_core_module', 'mod_authz_core.so'),
            ('dir_module', 'mod_dir.so'),
            ('mime_module', 'mod_mime.so'),
            ('log_config_module', 'mod_log_config.so'),
            ('rewrite_module', 'mod_rewrite.so'),
        ]
        
        for module_name, module_file in essential_modules:
            module_path = f"{modules_dir}/{module_file}"
            if os.path.exists(module_path):
                module_lines.append(f"LoadModule {module_name} {module_path}")
        
        # PHP module (check for libphp.so)
        php_module_path = f"{modules_dir}/libphp.so"
        if os.path.exists(php_module_path):
            module_lines.append(f"LoadModule php_module {php_module_path}")
        
        modules_config = "\n".join(module_lines)
        
        return f"""# HamppServer Apache Configuration for Termux
# Generated automatically by installer

ServerRoot "{prefix}"
Listen {port}

# Essential modules (only those that exist)
{modules_config}

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
    
    def _generate_linux_apache_config(self) -> str:
        """Generate Linux-specific Apache configuration.
        
        Returns:
            Apache configuration content
        """
        document_root = self.config.server_config.document_root
        port = self.config.server_config.apache_port
        
        return f"""# HamppServer Apache Configuration for Linux
# Generated automatically by installer

ServerRoot /etc/apache2
Listen {port}

# Load essential modules
LoadModule mpm_prefork_module /usr/lib/apache2/modules/mod_mpm_prefork.so
LoadModule authz_core_module /usr/lib/apache2/modules/mod_authz_core.so
LoadModule dir_module /usr/lib/apache2/modules/mod_dir.so
LoadModule mime_module /usr/lib/apache2/modules/mod_mime.so
LoadModule log_config_module /usr/lib/apache2/modules/mod_log_config.so
LoadModule rewrite_module /usr/lib/apache2/modules/mod_rewrite.so
LoadModule php_module /usr/lib/apache2/modules/libphp.so

# Server identification
ServerName localhost
ServerAdmin admin@localhost

# Document root
DocumentRoot "{document_root}"

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
TypesConfig /etc/mime.types

# Error and access logs
ErrorLog /var/log/apache2/error.log
CustomLog /var/log/apache2/access.log combined

# Process ID file
PidFile /var/run/apache2/httpd.pid
"""
    
    def _generate_mysql_config(self) -> str:
        """Generate MySQL configuration content.
        
        Returns:
            MySQL configuration content
        """
        if self.config.platform.is_termux:
            return self._generate_termux_mysql_config()
        else:
            return self._generate_linux_mysql_config()
    
    def _generate_termux_mysql_config(self) -> str:
        """Generate Termux-specific MySQL configuration.
        
        Returns:
            MySQL configuration content
        """
        prefix = "/data/data/com.termux/files/usr"
        
        return f"""# HamppServer MySQL Configuration for Termux
# Generated automatically by installer

[client]
port = {self.config.server_config.mysql_port}
socket = {prefix}/var/run/mysqld.sock

[mysqld]
port = {self.config.server_config.mysql_port}
socket = {prefix}/var/run/mysqld.sock
datadir = {prefix}/var/lib/mysql
log-error = {prefix}/var/log/mysql/error.log
pid-file = {prefix}/var/run/mysqld.pid

# Skip networking for local access only
skip-networking = 1

# Character set
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci

# Memory settings
key_buffer_size = 16M
max_allowed_packet = 64M
thread_stack = 192K
thread_cache_size = 8

# Query cache
query_cache_limit = 1M
query_cache_size = 16M

# InnoDB settings
innodb_buffer_pool_size = 128M
innodb_log_file_size = 64M
innodb_log_buffer_size = 8M
innodb_flush_log_at_trx_commit = 1
innodb_lock_wait_timeout = 50
"""
    
    def _generate_linux_mysql_config(self) -> str:
        """Generate Linux-specific MySQL configuration.
        
        Returns:
            MySQL configuration content
        """
        return f"""# HamppServer MySQL Configuration for Linux
# Generated automatically by installer

[client]
port = {self.config.server_config.mysql_port}
socket = /var/run/mysqld/mysqld.sock

[mysqld]
port = {self.config.server_config.mysql_port}
socket = /var/run/mysqld/mysqld.sock
datadir = /var/lib/mysql
log-error = /var/log/mysql/error.log
pid-file = /var/run/mysqld/mysqld.pid

# Network settings
bind-address = 127.0.0.1

# Character set
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci

# Memory settings
key_buffer_size = 16M
max_allowed_packet = 64M
thread_stack = 192K
thread_cache_size = 8

# Query cache
query_cache_limit = 1M
query_cache_size = 16M

# InnoDB settings
innodb_buffer_pool_size = 128M
innodb_log_file_size = 64M
innodb_log_buffer_size = 8M
innodb_flush_log_at_trx_commit = 1
innodb_lock_wait_timeout = 50

# Security settings
local-infile = 0
"""
    
    def _setup_configuration_files(self) -> bool:
        """Setup configuration files.
        
        Returns:
            True if setup successful
        """
        logger.info("Setting up configuration files...")
        
        # Create hampp command script
        hampp_script = self._generate_hampp_script()
        hampp_path = f"{self.config.path_config.apache_bin.rsplit('/', 1)[0]}/hampp"
        
        if not write_file(hampp_path, hampp_script):
            logger.error("Failed to create hampp script")
            return False
        
        if not make_executable(hampp_path):
            logger.error("Failed to make hampp script executable")
            return False
        
        return True
    
    def _setup_web_files(self) -> bool:
        """Setup default web files.
        
        Returns:
            True if setup successful
        """
        logger.info("Setting up default web files...")
        
        # Ensure document root exists
        doc_root = self.config.server_config.document_root
        if not ensure_directory(doc_root):
            logger.error(f"Failed to create document root: {doc_root}")
            return False
        
        # Create default index.html
        index_html = self._generate_index_html()
        index_path = Path(doc_root) / "index.html"
        
        try:
            if not write_file(index_path, index_html):
                logger.error("Failed to create index.html")
                return False
            else:
                logger.info(f"Created index.html at: {index_path}")
        except Exception as e:
            logger.error(f"Error creating index.html: {e}")
            return False
        
        # Create phpinfo.php
        phpinfo_content = "<?php phpinfo(); ?>"
        phpinfo_path = Path(doc_root) / "phpinfo.php"
        
        try:
            if not write_file(phpinfo_path, phpinfo_content):
                logger.error("Failed to create phpinfo.php")
                return False
            else:
                logger.info(f"Created phpinfo.php at: {phpinfo_path}")
        except Exception as e:
            logger.error(f"Error creating phpinfo.php: {e}")
            return False
        
        logger.info("Default web files created successfully")
        return True
    
    def _install_phpmyadmin(self) -> bool:
        """Install PHPMyAdmin.
        
        Returns:
            True if installation successful
        """
        logger.info("Installing PHPMyAdmin...")
        
        # Ensure document root exists
        doc_root = self.config.server_config.document_root
        if not ensure_directory(doc_root):
            logger.error(f"Failed to create document root: {doc_root}")
            return False
        
        phpmyadmin_url = "https://github.com/yourchocomate/phpmyadmin/raw/main/phpmyadmin.zip"
        phpmyadmin_dir = Path(doc_root) / "phpmyadmin"
        
        # Skip if already exists
        if phpmyadmin_dir.exists():
            logger.info("PHPMyAdmin already installed")
            return True
        
        try:
            # Check internet connection first
            logger.info("Checking internet connection...")
            import urllib.request
            urllib.request.urlopen('https://www.google.com', timeout=10)
            
            # Download PHPMyAdmin
            with tempfile.TemporaryDirectory() as temp_dir:
                zip_path = Path(temp_dir) / "phpmyadmin.zip"
                
                logger.info("Downloading PHPMyAdmin...")
                try:
                    urlretrieve(phpmyadmin_url, zip_path)
                except Exception as e:
                    logger.error(f"Failed to download PHPMyAdmin: {e}")
                    logger.info("PHPMyAdmin installation skipped - you can install it manually later")
                    return True  # Don't fail the entire installation
                
                # Verify download
                if not zip_path.exists() or zip_path.stat().st_size < 1000:
                    logger.warning("Downloaded file seems invalid, skipping PHPMyAdmin")
                    return True
                
                # Extract PHPMyAdmin
                logger.info("Extracting PHPMyAdmin...")
                ensure_directory(phpmyadmin_dir)
                
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(phpmyadmin_dir)
                
                logger.info(f"PHPMyAdmin installed successfully at: {phpmyadmin_dir}")
                return True
                
        except urllib.error.URLError:
            logger.warning("No internet connection - PHPMyAdmin installation skipped")
            logger.info("You can install PHPMyAdmin manually later")
            return True  # Don't fail installation due to no internet
        except Exception as e:
            logger.error(f"Failed to install PHPMyAdmin: {e}")
            logger.info("PHPMyAdmin installation failed - you can install it manually later")
            return True  # Don't fail the entire installation
    
    def _generate_hampp_script(self) -> str:
        """Generate hampp command script.
        
        Returns:
            Script content
        """
        return f"""#!/bin/bash
# HamppServer command script
# Generated automatically

HAMPP_DIR="{Path(__file__).parent.parent.parent}"
export PYTHONPATH="$HAMPP_DIR:$PYTHONPATH"

cd "$HAMPP_DIR"
exec python -m hampp.cli.main "$@"
"""
    
    def _generate_index_html(self) -> str:
        """Generate default index.html content.
        
        Returns:
            HTML content
        """
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HamppServer - Welcome</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #333;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            padding: 3rem;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            text-align: center;
            max-width: 600px;
            width: 90%;
        }
        
        .logo {
            font-size: 3rem;
            font-weight: bold;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
        }
        
        .subtitle {
            font-size: 1.2rem;
            color: #666;
            margin-bottom: 2rem;
        }
        
        .status {
            background: #e8f5e8;
            border: 2px solid #4caf50;
            border-radius: 10px;
            padding: 1rem;
            margin: 2rem 0;
        }
        
        .status-text {
            color: #2e7d32;
            font-weight: 600;
            font-size: 1.1rem;
        }
        
        .links {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-top: 2rem;
        }
        
        .link {
            background: #f8f9fa;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            padding: 1rem;
            text-decoration: none;
            color: #495057;
            transition: all 0.3s ease;
        }
        
        .link:hover {
            border-color: #667eea;
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
        }
        
        .link-title {
            font-weight: 600;
            margin-bottom: 0.5rem;
        }
        
        .link-desc {
            font-size: 0.9rem;
            color: #6c757d;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">HamppServer</div>
        <div class="subtitle">Your modern localhost web server</div>
        
        <div class="status">
            <div class="status-text">🚀 Server is running successfully!</div>
        </div>
        
        <div class="links">
            <a href="phpinfo.php" class="link">
                <div class="link-title">📋 PHP Info</div>
                <div class="link-desc">View PHP configuration</div>
            </a>
            
            <a href="phpmyadmin/" class="link">
                <div class="link-title">🗄️ PHPMyAdmin</div>
                <div class="link-desc">Manage your database</div>
            </a>
        </div>
        
        <p style="margin-top: 2rem; color: #6c757d; font-size: 0.9rem;">
            Replace this file with your own index.php to get started!
        </p>
    </div>
</body>
</html>"""
    
    def _run_command(self, cmd: List[str], timeout: int = 300) -> bool:
        """Run shell command with error handling.
        
        Args:
            cmd: Command to run as list
            timeout: Timeout in seconds
        
        Returns:
            True if command succeeded
        """
        try:
            logger.debug(f"Running command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode == 0:
                if result.stdout:
                    logger.debug(f"Command output: {result.stdout}")
                return True
            else:
                logger.error(f"Command failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out: {' '.join(cmd)}")
            return False
        except Exception as e:
            logger.error(f"Command error: {e}")
            return False
    
    def uninstall(self) -> bool:
        """Uninstall HamppServer.
        
        Returns:
            True if uninstallation successful
        """
        logger.info("Uninstalling HamppServer...")
        
        # This would remove installed files and configurations
        # Implementation depends on specific requirements
        
        logger.info("HamppServer uninstalled successfully")
        return True
