"""Platform detection utilities for HamppServer."""

import os
import platform
import subprocess
from typing import Optional

from hampp.utils.logger import setup_logger

logger = setup_logger(__name__)


class PlatformDetector:
    """Detects and provides information about the current platform."""
    
    def __init__(self):
        """Initialize platform detector."""
        self._platform_info = None
        self._detect_platform()
    
    def _detect_platform(self) -> None:
        """Detect current platform and gather information."""
        system = platform.system().lower()
        
        self._platform_info = {
            'system': system,
            'machine': platform.machine(),
            'processor': platform.processor(),
            'version': platform.version(),
            'python_version': platform.python_version(),
        }
        
        # Detect specific environments
        self._detect_termux()
        self._detect_android()
        self._detect_linux_distro()
        
        logger.info(f"Detected platform: {self.name}")
    
    def _detect_termux(self) -> None:
        """Detect if running in Termux environment."""
        termux_indicators = [
            os.environ.get('TERMUX_VERSION'),
            os.path.exists('/data/data/com.termux'),
            os.path.exists('/data/data/com.termux/files/usr/bin/pkg'),
        ]
        
        self._platform_info['is_termux'] = any(termux_indicators)
        
        if self.is_termux:
            # Get Termux-specific info
            try:
                result = subprocess.run(['pkg', '--version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    self._platform_info['termux_version'] = result.stdout.strip()
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
    
    def _detect_android(self) -> None:
        """Detect if running on Android."""
        android_indicators = [
            self.is_termux,
            os.path.exists('/system/build.prop'),
            os.path.exists('/system/bin/getprop'),
            os.environ.get('ANDROID_ROOT'),
        ]
        
        self._platform_info['is_android'] = any(android_indicators)
        
        if self.is_android:
            # Get Android version if possible
            try:
                result = subprocess.run(['getprop', 'ro.build.version.release'],
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    self._platform_info['android_version'] = result.stdout.strip()
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
    
    def _detect_linux_distro(self) -> None:
        """Detect Linux distribution."""
        if self.system != 'linux':
            self._platform_info['is_linux'] = False
            return
        
        self._platform_info['is_linux'] = True
        
        # Try to detect distribution
        distro_info = {}
        
        # Try /etc/os-release first (standard)
        if os.path.exists('/etc/os-release'):
            try:
                with open('/etc/os-release', 'r') as f:
                    for line in f:
                        if '=' in line:
                            key, value = line.strip().split('=', 1)
                            distro_info[key] = value.strip('"')
            except Exception as e:
                logger.debug(f"Error reading /etc/os-release: {e}")
        
        # Try lsb_release command
        if not distro_info:
            try:
                result = subprocess.run(['lsb_release', '-a'],
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if ':' in line:
                            key, value = line.split(':', 1)
                            distro_info[key.strip()] = value.strip()
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
        
        self._platform_info['distro'] = distro_info
    
    @property
    def name(self) -> str:
        """Get human-readable platform name."""
        if self.is_termux:
            return "Termux (Android)"
        elif self.is_android:
            return "Android"
        elif self.is_linux:
            distro = self._platform_info.get('distro', {})
            distro_name = (distro.get('NAME') or 
                          distro.get('PRETTY_NAME') or 
                          distro.get('Distributor ID') or 
                          'Linux')
            return distro_name
        else:
            return self.system.title()
    
    @property
    def system(self) -> str:
        """Get system name (linux, darwin, windows, etc.)."""
        return self._platform_info['system']
    
    @property
    def is_termux(self) -> bool:
        """Check if running in Termux."""
        return self._platform_info.get('is_termux', False)
    
    @property
    def is_android(self) -> bool:
        """Check if running on Android."""
        return self._platform_info.get('is_android', False)
    
    @property
    def is_linux(self) -> bool:
        """Check if running on Linux."""
        return self._platform_info.get('is_linux', False)
    
    @property
    def is_darwin(self) -> bool:
        """Check if running on macOS."""
        return self.system == 'darwin'
    
    @property
    def is_windows(self) -> bool:
        """Check if running on Windows."""
        return self.system == 'windows'
    
    @property
    def is_supported(self) -> bool:
        """Check if platform is supported."""
        return self.is_termux or self.is_linux or self.is_darwin
    
    def get_package_manager(self) -> Optional[str]:
        """Get the system's package manager."""
        if self.is_termux:
            return 'pkg'
        elif self.is_linux:
            # Check for various package managers
            managers = [
                ('apt', '/usr/bin/apt'),
                ('yum', '/usr/bin/yum'),
                ('dnf', '/usr/bin/dnf'),
                ('pacman', '/usr/bin/pacman'),
                ('zypper', '/usr/bin/zypper'),
                ('emerge', '/usr/bin/emerge'),
            ]
            
            for manager, path in managers:
                if os.path.exists(path):
                    return manager
        elif self.is_darwin:
            if os.path.exists('/usr/local/bin/brew'):
                return 'brew'
            elif os.path.exists('/opt/local/bin/port'):
                return 'port'
        
        return None
    
    def check_dependencies(self) -> dict:
        """Check if required dependencies are available."""
        dependencies = {
            'apache': self._check_command('apachectl') or self._check_command('httpd'),
            'mysql': self._check_command('mysqld') or self._check_command('mariadb') or self._check_command('mysql'),
            'php': self._check_command('php'),
            'python': self._check_command('python3') or self._check_command('python'),
        }
        
        # Check for specific Termux paths
        if self.is_termux:
            termux_prefix = "/data/data/com.termux/files/usr"
            dependencies.update({
                'apache': os.path.exists(f"{termux_prefix}/bin/httpd") or os.path.exists(f"{termux_prefix}/bin/apachectl"),
                'mysql': os.path.exists(f"{termux_prefix}/bin/mysqld") or os.path.exists(f"{termux_prefix}/bin/mariadbd"),
                'php': os.path.exists(f"{termux_prefix}/bin/php"),
            })
        
        return dependencies
    
    def _check_command(self, command: str) -> bool:
        """Check if a command is available in PATH."""
        try:
            subprocess.run([command, '--version'], 
                          capture_output=True, timeout=5)
            return True
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
            return False
    
    def get_info(self) -> dict:
        """Get complete platform information."""
        info = self._platform_info.copy()
        info.update({
            'name': self.name,
            'package_manager': self.get_package_manager(),
            'dependencies': self.check_dependencies(),
            'supported': self.is_supported,
        })
        return info
