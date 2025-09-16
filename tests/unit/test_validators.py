"""Unit tests for input validators."""

import pytest
import tempfile
import os
from pathlib import Path

from hampp.utils.validators import (
    validate_port,
    validate_directory,
    validate_php_version,
    validate_config_value,
    sanitize_filename
)


class TestValidatePort:
    """Test port validation."""
    
    def test_valid_ports(self):
        """Test validation of valid ports."""
        test_cases = [
            ("8080", True, 8080),
            ("3306", True, 3306),
            ("80", True, 80),
            ("65535", True, 65535),
        ]
        
        for port_str, expected_valid, expected_port in test_cases:
            valid, port, error = validate_port(port_str)
            assert valid == expected_valid
            if expected_valid:
                assert port == expected_port
                assert error == ""
    
    def test_invalid_ports(self):
        """Test validation of invalid ports."""
        test_cases = [
            "0",      # Too low
            "65536",  # Too high
            "-1",     # Negative
            "abc",    # Not a number
            "8080.5", # Decimal
            "",       # Empty
        ]
        
        for port_str in test_cases:
            valid, port, error = validate_port(port_str)
            assert valid is False
            assert port is None
            assert error != ""
    
    def test_system_ports(self):
        """Test validation of system ports."""
        # Mock os.geteuid to return non-root
        with pytest.mock.patch('os.geteuid', return_value=1000):
            valid, port, error = validate_port("80")
            assert valid is False
            assert "root privileges" in error


class TestValidateDirectory:
    """Test directory validation."""
    
    def test_valid_existing_directory(self, temp_dir):
        """Test validation of existing directory."""
        valid, error = validate_directory(str(temp_dir))
        assert valid is True
        assert error == ""
    
    def test_valid_new_directory(self, temp_dir):
        """Test validation of new directory."""
        new_dir = temp_dir / "new_directory"
        valid, error = validate_directory(str(new_dir))
        assert valid is True
        assert error == ""
        assert new_dir.exists()
    
    def test_invalid_empty_path(self):
        """Test validation of empty directory path."""
        valid, error = validate_directory("")
        assert valid is False
        assert "cannot be empty" in error
    
    def test_invalid_file_as_directory(self, temp_dir):
        """Test validation when path is a file, not directory."""
        file_path = temp_dir / "test_file.txt"
        file_path.write_text("test")
        
        valid, error = validate_directory(str(file_path))
        assert valid is False
        assert "not a directory" in error


class TestValidatePhpVersion:
    """Test PHP version validation."""
    
    def test_valid_versions(self):
        """Test validation of valid PHP versions."""
        test_cases = [
            "auto",
            "7.4",
            "8.0",
            "8.1",
            "8.2",
            "5.6",
        ]
        
        for version in test_cases:
            valid, error = validate_php_version(version)
            assert valid is True
            assert error == ""
    
    def test_invalid_versions(self):
        """Test validation of invalid PHP versions."""
        test_cases = [
            "7",      # Missing minor version
            "8.1.0",  # Too specific
            "4.0",    # Too old
            "10.0",   # Too new
            "abc",    # Not a version
            "",       # Empty
        ]
        
        for version in test_cases:
            valid, error = validate_php_version(version)
            assert valid is False
            assert error != ""


class TestValidateConfigValue:
    """Test configuration value validation."""
    
    def test_valid_config_values(self):
        """Test validation of valid configuration values."""
        test_cases = [
            ("apache_port", "8080", True, 8080),
            ("mysql_port", "3306", True, 3306),
            ("php_version", "auto", True, "auto"),
            ("enable_phpmyadmin", "true", True, True),
            ("auto_start_services", "false", True, False),
        ]
        
        for key, value, expected_valid, expected_value in test_cases:
            with pytest.mock.patch('hampp.utils.validators.validate_directory', return_value=(True, "")):
                valid, result, error = validate_config_value(key, value)
                assert valid == expected_valid
                if expected_valid:
                    assert result == expected_value
                    assert error == ""
    
    def test_invalid_config_key(self):
        """Test validation with invalid configuration key."""
        valid, result, error = validate_config_value("invalid_key", "value")
        assert valid is False
        assert result is None
        assert "Unknown configuration key" in error


class TestSanitizeFilename:
    """Test filename sanitization."""
    
    def test_valid_filename(self):
        """Test sanitization of already valid filename."""
        filename = "valid_filename.txt"
        result = sanitize_filename(filename)
        assert result == filename
    
    def test_invalid_characters(self):
        """Test sanitization of filename with invalid characters."""
        filename = "file<>:\"/\\|?*name.txt"
        result = sanitize_filename(filename)
        assert "<" not in result
        assert ">" not in result
        assert ":" not in result
        assert "\"" not in result
        assert "/" not in result
        assert "\\" not in result
        assert "|" not in result
        assert "?" not in result
        assert "*" not in result
    
    def test_empty_filename(self):
        """Test sanitization of empty filename."""
        result = sanitize_filename("")
        assert result == "unnamed"
    
    def test_long_filename(self):
        """Test sanitization of very long filename."""
        long_filename = "a" * 300
        result = sanitize_filename(long_filename)
        assert len(result) <= 255
