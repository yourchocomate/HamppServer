"""Configuration management for HamppServer."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

from hampp.core.platform_detector import PlatformDetector
from hampp.utils.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class ServerConfig:
    """Server configuration settings."""
    
    apache_port: int = 8080
    mysql_port: int = 3306
    document_root: str = ""
    php_version: str = "auto"
    enable_phpmyadmin: bool = True
    auto_start_services: bool = False


@dataclass
class PathConfig:
    """Platform-specific path configuration."""
    
    apache_bin: str = ""
    apache_config: str = ""
    mysql_bin: str = ""
    mysql_config: str = ""
    php_bin: str = ""
    document_root: str = ""
    log_dir: str = ""
    pid_dir: str = ""


class Config:
    """Main configuration manager for HamppServer."""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize configuration manager.
        
        Args:
            config_file: Optional custom config file path
        """
        self.platform = PlatformDetector()
        self.config_file = config_file or self._get_default_config_file()
        self.server_config = ServerConfig()
        self.path_config = PathConfig()
        
        self._load_config()
        self._setup_platform_paths()
    
    def _get_default_config_file(self) -> str:
        """Get default config file path based on platform."""
        if self.platform.is_termux:
            config_dir = Path("/data/data/com.termux/files/home/.config/hampp")
        else:
            config_dir = Path.home() / ".config" / "hampp"
        
        config_dir.mkdir(parents=True, exist_ok=True)
        return str(config_dir / "config.yaml")
    
    def _load_config(self) -> None:
        """Load configuration from file."""
        if not os.path.exists(self.config_file):
            logger.info(f"Config file not found at {self.config_file}, using defaults")
            self._save_config()
            return
        
        try:
            with open(self.config_file, 'r') as f:
                config_data = yaml.safe_load(f) or {}
            
            # Update server config
            server_data = config_data.get('server', {})
            for key, value in server_data.items():
                if hasattr(self.server_config, key):
                    setattr(self.server_config, key, value)
            
            # Update path config  
            path_data = config_data.get('paths', {})
            for key, value in path_data.items():
                if hasattr(self.path_config, key):
                    setattr(self.path_config, key, value)
                    
            logger.info(f"Configuration loaded from {self.config_file}")
            
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            logger.info("Using default configuration")
    
    def _save_config(self) -> None:
        """Save current configuration to file."""
        try:
            config_data = {
                'server': asdict(self.server_config),
                'paths': asdict(self.path_config)
            }
            
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                yaml.dump(config_data, f, default_flow_style=False, indent=2)
            
            logger.info(f"Configuration saved to {self.config_file}")
            
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    def _setup_platform_paths(self) -> None:
        """Setup platform-specific paths."""
        if self.platform.is_termux:
            self._setup_termux_paths()
        elif self.platform.is_linux:
            self._setup_linux_paths()
        else:
            self._setup_generic_paths()
        
        # Set document root if not configured
        if not self.server_config.document_root:
            self.server_config.document_root = self.path_config.document_root
    
    def _setup_termux_paths(self) -> None:
        """Setup Termux-specific paths."""
        prefix = "/data/data/com.termux/files/usr"
        
        # Check which binaries actually exist
        if os.path.exists(f"{prefix}/bin/httpd"):
            self.path_config.apache_bin = f"{prefix}/bin/httpd"
        elif os.path.exists(f"{prefix}/bin/apachectl"):
            self.path_config.apache_bin = f"{prefix}/bin/apachectl"
        else:
            self.path_config.apache_bin = f"{prefix}/bin/httpd"
        
        self.path_config.apache_config = f"{prefix}/etc/apache2/httpd.conf"
        
        # Check for MySQL/MariaDB binaries
        if os.path.exists(f"{prefix}/bin/mariadbd"):
            self.path_config.mysql_bin = f"{prefix}/bin/mariadbd"
        elif os.path.exists(f"{prefix}/bin/mysqld"):
            self.path_config.mysql_bin = f"{prefix}/bin/mysqld"
        else:
            self.path_config.mysql_bin = f"{prefix}/bin/mariadbd"
        
        self.path_config.mysql_config = f"{prefix}/etc/my.cnf"
        self.path_config.php_bin = f"{prefix}/bin/php"
        self.path_config.document_root = "/sdcard/www"
        self.path_config.log_dir = f"{prefix}/var/log"
        self.path_config.pid_dir = f"{prefix}/var/run"
    
    def _setup_linux_paths(self) -> None:
        """Setup Linux-specific paths."""
        self.path_config.apache_bin = "/usr/bin/apachectl"
        self.path_config.apache_config = "/etc/apache2/apache2.conf"
        self.path_config.mysql_bin = "/usr/bin/mysqld"
        self.path_config.mysql_config = "/etc/mysql/my.cnf"
        self.path_config.php_bin = "/usr/bin/php"
        self.path_config.document_root = str(Path.home() / "www")
        self.path_config.log_dir = "/var/log"
        self.path_config.pid_dir = "/var/run"
    
    def _setup_generic_paths(self) -> None:
        """Setup generic Unix paths."""
        self.path_config.apache_bin = "apachectl"
        self.path_config.apache_config = "/usr/local/etc/apache2/httpd.conf"
        self.path_config.mysql_bin = "mysqld"
        self.path_config.mysql_config = "/usr/local/etc/my.cnf"
        self.path_config.php_bin = "php"
        self.path_config.document_root = str(Path.home() / "www")
        self.path_config.log_dir = "/usr/local/var/log"
        self.path_config.pid_dir = "/usr/local/var/run"
    
    def update_server_config(self, **kwargs) -> None:
        """Update server configuration.
        
        Args:
            **kwargs: Configuration key-value pairs to update
        """
        for key, value in kwargs.items():
            if hasattr(self.server_config, key):
                setattr(self.server_config, key, value)
                logger.info(f"Updated {key} = {value}")
            else:
                logger.warning(f"Unknown configuration key: {key}")
        
        self._save_config()
    
    def get_config_dict(self) -> Dict[str, Any]:
        """Get configuration as dictionary.
        
        Returns:
            Dictionary containing all configuration
        """
        return {
            'server': asdict(self.server_config),
            'paths': asdict(self.path_config),
            'platform': {
                'name': self.platform.name,
                'is_termux': self.platform.is_termux,
                'is_linux': self.platform.is_linux,
                'is_android': self.platform.is_android,
            }
        }
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults."""
        self.server_config = ServerConfig()
        self.path_config = PathConfig()
        self._setup_platform_paths()
        self._save_config()
        logger.info("Configuration reset to defaults")
