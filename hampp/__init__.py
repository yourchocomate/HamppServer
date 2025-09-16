"""
HamppServer - A modern, cross-platform local server manager.

A complete localhost server manager for Apache, MariaDB/MySQL, and PHP
with support for Termux (Android), Linux, and other Unix-like systems.
"""

__version__ = "2.0.0"
__author__ = "Md Habibur Rahman"
__email__ = "yourchocomate@gmail.com"
__license__ = "MIT"

from hampp.core.config import Config
from hampp.core.server_manager import ServerManager

__all__ = ["Config", "ServerManager", "__version__"]
