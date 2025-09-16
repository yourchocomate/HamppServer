"""Input validation utilities for HamppServer."""

import os
import re
from pathlib import Path
from typing import Tuple, Optional

from hampp.utils.logger import setup_logger

logger = setup_logger(__name__)


def validate_port(port: str) -> Tuple[bool, Optional[int], str]:
    """Validate port number.
    
    Args:
        port: Port number as string
    
    Returns:
        Tuple of (is_valid, port_int, error_message)
    """
    try:
        port_int = int(port)
        
        if port_int < 1 or port_int > 65535:
            return False, None, "Port must be between 1 and 65535"
        
        if port_int < 1024 and os.geteuid() != 0:
            return False, None, "Port numbers below 1024 require root privileges"
        
        # Check for commonly used system ports
        system_ports = {
            22: "SSH",
            25: "SMTP", 
            53: "DNS",
            80: "HTTP",
            110: "POP3",
            143: "IMAP",
            443: "HTTPS",
            993: "IMAPS",
            995: "POP3S"
        }
        
        if port_int in system_ports:
            logger.warning(f"Port {port_int} is commonly used for {system_ports[port_int]}")
        
        return True, port_int, ""
        
    except ValueError:
        return False, None, "Port must be a valid number"


def validate_directory(directory: str) -> Tuple[bool, str]:
    """Validate directory path.
    
    Args:
        directory: Directory path to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not directory:
        return False, "Directory path cannot be empty"
    
    try:
        path = Path(directory).resolve()
        
        # Check if path exists
        if not path.exists():
            try:
                path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created directory: {path}")
            except PermissionError:
                return False, f"Permission denied: Cannot create directory {path}"
            except Exception as e:
                return False, f"Cannot create directory {path}: {e}"
        
        # Check if it's actually a directory
        if not path.is_dir():
            return False, f"Path exists but is not a directory: {path}"
        
        # Check if we can write to it
        if not os.access(path, os.W_OK):
            return False, f"No write permission for directory: {path}"
        
        return True, ""
        
    except Exception as e:
        return False, f"Invalid directory path: {e}"


def validate_php_version(version: str) -> Tuple[bool, str]:
    """Validate PHP version string.
    
    Args:
        version: PHP version (e.g., "7.4", "8.1", "auto")
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if version.lower() == "auto":
        return True, ""
    
    # Match version pattern like 7.4, 8.1, etc.
    version_pattern = r'^\d+\.\d+$'
    
    if not re.match(version_pattern, version):
        return False, "PHP version must be in format 'X.Y' (e.g., '8.1') or 'auto'"
    
    # Check if version is reasonable
    major, minor = map(int, version.split('.'))
    
    if major < 5 or major > 9:
        return False, "PHP major version must be between 5 and 9"
    
    if minor < 0 or minor > 9:
        return False, "PHP minor version must be between 0 and 9"
    
    return True, ""


def validate_config_value(key: str, value: str) -> Tuple[bool, any, str]:
    """Validate configuration value based on key.
    
    Args:
        key: Configuration key
        value: Value to validate
    
    Returns:
        Tuple of (is_valid, converted_value, error_message)
    """
    validators = {
        'apache_port': lambda v: validate_port(v),
        'mysql_port': lambda v: validate_port(v),
        'document_root': lambda v: (validate_directory(v)[0], v, validate_directory(v)[1]),
        'php_version': lambda v: (validate_php_version(v)[0], v, validate_php_version(v)[1]),
        'enable_phpmyadmin': lambda v: _validate_boolean(v),
        'auto_start_services': lambda v: _validate_boolean(v),
    }
    
    if key not in validators:
        return False, None, f"Unknown configuration key: {key}"
    
    try:
        return validators[key](value)
    except Exception as e:
        return False, None, f"Validation error for {key}: {e}"


def _validate_boolean(value: str) -> Tuple[bool, bool, str]:
    """Validate boolean value from string.
    
    Args:
        value: String value to convert to boolean
    
    Returns:
        Tuple of (is_valid, boolean_value, error_message)
    """
    if isinstance(value, bool):
        return True, value, ""
    
    if isinstance(value, str):
        lower_val = value.lower()
        if lower_val in ('true', 't', 'yes', 'y', '1', 'on'):
            return True, True, ""
        elif lower_val in ('false', 'f', 'no', 'n', '0', 'off'):
            return True, False, ""
    
    return False, None, f"Invalid boolean value: {value}. Use true/false, yes/no, 1/0, or on/off"


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for cross-platform compatibility.
    
    Args:
        filename: Original filename
    
    Returns:
        Sanitized filename
    """
    # Remove or replace invalid characters
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '_', filename)
    
    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip('. ')
    
    # Ensure filename is not empty
    if not sanitized:
        sanitized = "unnamed"
    
    # Limit length
    if len(sanitized) > 255:
        sanitized = sanitized[:255]
    
    return sanitized
