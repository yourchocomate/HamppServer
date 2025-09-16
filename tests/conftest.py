"""Test configuration and fixtures for HamppServer tests."""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

from hampp.core.config import Config
from hampp.core.server_manager import ServerManager
from hampp.core.installer import Installer
from hampp.core.platform_detector import PlatformDetector


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)


@pytest.fixture
def mock_platform():
    """Mock platform detector for consistent testing."""
    with patch('hampp.core.platform_detector.PlatformDetector') as mock:
        platform = Mock()
        platform.is_termux = False
        platform.is_linux = True
        platform.is_android = False
        platform.is_darwin = False
        platform.is_windows = False
        platform.is_supported = True
        platform.name = "Test Linux"
        platform.system = "linux"
        platform.get_package_manager.return_value = "apt"
        platform.check_dependencies.return_value = {
            'apache': True,
            'mysql': True,
            'php': True,
            'python': True
        }
        mock.return_value = platform
        yield platform


@pytest.fixture
def test_config(temp_dir, mock_platform):
    """Create a test configuration."""
    config_file = temp_dir / "test_config.yaml"
    config = Config(str(config_file))
    
    # Override paths for testing
    config.path_config.apache_bin = "/usr/bin/apachectl"
    config.path_config.apache_config = str(temp_dir / "apache.conf")
    config.path_config.mysql_bin = "/usr/bin/mysqld"
    config.path_config.document_root = str(temp_dir / "www")
    config.path_config.log_dir = str(temp_dir / "logs")
    config.path_config.pid_dir = str(temp_dir / "pids")
    
    # Create directories
    (temp_dir / "www").mkdir()
    (temp_dir / "logs").mkdir()
    (temp_dir / "pids").mkdir()
    
    return config


@pytest.fixture
def server_manager(test_config):
    """Create a test server manager."""
    return ServerManager(test_config)


@pytest.fixture
def installer(test_config):
    """Create a test installer."""
    return Installer(test_config)


@pytest.fixture
def mock_subprocess():
    """Mock subprocess calls."""
    with patch('subprocess.run') as mock:
        # Default successful return
        mock.return_value.returncode = 0
        mock.return_value.stdout = ""
        mock.return_value.stderr = ""
        yield mock


@pytest.fixture
def mock_requests():
    """Mock requests for HTTP calls."""
    with patch('requests.get') as mock:
        response = Mock()
        response.status_code = 200
        response.headers = {'server': 'Apache/2.4.0'}
        mock.return_value = response
        yield mock


@pytest.fixture
def mock_psutil():
    """Mock psutil for process management."""
    with patch('psutil.pid_exists') as pid_exists, \
         patch('psutil.process_iter') as process_iter, \
         patch('psutil.net_connections') as net_connections:
        
        pid_exists.return_value = True
        process_iter.return_value = []
        net_connections.return_value = []
        
        yield {
            'pid_exists': pid_exists,
            'process_iter': process_iter,
            'net_connections': net_connections
        }
