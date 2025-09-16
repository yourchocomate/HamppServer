"""Unit tests for configuration management."""

import pytest
import yaml
from pathlib import Path

from hampp.core.config import Config, ServerConfig, PathConfig


class TestServerConfig:
    """Test ServerConfig dataclass."""
    
    def test_default_values(self):
        """Test default configuration values."""
        config = ServerConfig()
        
        assert config.apache_port == 8080
        assert config.mysql_port == 3306
        assert config.document_root == ""
        assert config.php_version == "auto"
        assert config.enable_phpmyadmin is True
        assert config.auto_start_services is False


class TestPathConfig:
    """Test PathConfig dataclass."""
    
    def test_default_values(self):
        """Test default path configuration values."""
        config = PathConfig()
        
        assert config.apache_bin == ""
        assert config.apache_config == ""
        assert config.mysql_bin == ""
        assert config.document_root == ""


class TestConfig:
    """Test main Config class."""
    
    def test_initialization(self, temp_dir, mock_platform):
        """Test configuration initialization."""
        config_file = temp_dir / "config.yaml"
        config = Config(str(config_file))
        
        assert config.config_file == str(config_file)
        assert isinstance(config.server_config, ServerConfig)
        assert isinstance(config.path_config, PathConfig)
    
    def test_load_empty_config(self, temp_dir, mock_platform):
        """Test loading when no config file exists."""
        config_file = temp_dir / "nonexistent.yaml"
        config = Config(str(config_file))
        
        # Should use defaults
        assert config.server_config.apache_port == 8080
        assert config.server_config.mysql_port == 3306
    
    def test_load_existing_config(self, temp_dir, mock_platform):
        """Test loading existing configuration file."""
        config_file = temp_dir / "config.yaml"
        
        # Create config file
        config_data = {
            'server': {
                'apache_port': 9090,
                'mysql_port': 3307,
                'enable_phpmyadmin': False
            },
            'paths': {
                'document_root': '/custom/www'
            }
        }
        
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        config = Config(str(config_file))
        
        assert config.server_config.apache_port == 9090
        assert config.server_config.mysql_port == 3307
        assert config.server_config.enable_phpmyadmin is False
        assert config.path_config.document_root == '/custom/www'
    
    def test_update_server_config(self, test_config):
        """Test updating server configuration."""
        test_config.update_server_config(
            apache_port=9090,
            enable_phpmyadmin=False
        )
        
        assert test_config.server_config.apache_port == 9090
        assert test_config.server_config.enable_phpmyadmin is False
    
    def test_get_config_dict(self, test_config):
        """Test getting configuration as dictionary."""
        config_dict = test_config.get_config_dict()
        
        assert 'server' in config_dict
        assert 'paths' in config_dict
        assert 'platform' in config_dict
        
        assert config_dict['server']['apache_port'] == 8080
        assert config_dict['platform']['is_linux'] is True
    
    def test_reset_to_defaults(self, test_config):
        """Test resetting configuration to defaults."""
        # Modify configuration
        test_config.update_server_config(apache_port=9090)
        assert test_config.server_config.apache_port == 9090
        
        # Reset to defaults
        test_config.reset_to_defaults()
        assert test_config.server_config.apache_port == 8080
