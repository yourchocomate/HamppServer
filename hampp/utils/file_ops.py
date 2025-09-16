"""File operation utilities for HamppServer."""

import os
import shutil
import stat
from pathlib import Path
from typing import Optional, Union

from hampp.utils.logger import setup_logger

logger = setup_logger(__name__)


def ensure_directory(path: Union[str, Path], mode: int = 0o755) -> bool:
    """Ensure directory exists with proper permissions.
    
    Args:
        path: Directory path to create
        mode: Directory permissions (octal)
    
    Returns:
        True if directory exists or was created successfully
    """
    try:
        path_obj = Path(path)
        path_obj.mkdir(parents=True, exist_ok=True)
        
        # Set permissions
        os.chmod(path_obj, mode)
        
        logger.debug(f"Directory ensured: {path_obj}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to ensure directory {path}: {e}")
        return False


def copy_file(src: Union[str, Path], dst: Union[str, Path], 
              preserve_permissions: bool = True) -> bool:
    """Copy file with error handling.
    
    Args:
        src: Source file path
        dst: Destination file path
        preserve_permissions: Whether to preserve file permissions
    
    Returns:
        True if file was copied successfully
    """
    try:
        src_path = Path(src)
        dst_path = Path(dst)
        
        if not src_path.exists():
            logger.error(f"Source file does not exist: {src_path}")
            return False
        
        # Ensure destination directory exists
        ensure_directory(dst_path.parent)
        
        # Copy file
        shutil.copy2(src_path, dst_path)
        
        # Set permissions if requested
        if preserve_permissions:
            src_stat = src_path.stat()
            os.chmod(dst_path, src_stat.st_mode)
        
        logger.debug(f"File copied: {src_path} -> {dst_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to copy file {src} -> {dst}: {e}")
        return False


def read_file(path: Union[str, Path], encoding: str = 'utf-8') -> Optional[str]:
    """Read file content with error handling.
    
    Args:
        path: File path to read
        encoding: File encoding
    
    Returns:
        File content as string, or None if failed
    """
    try:
        with open(path, 'r', encoding=encoding) as f:
            content = f.read()
        
        logger.debug(f"File read: {path}")
        return content
        
    except Exception as e:
        logger.error(f"Failed to read file {path}: {e}")
        return None


def write_file(path: Union[str, Path], content: str, 
               encoding: str = 'utf-8', mode: int = 0o644) -> bool:
    """Write file content with error handling.
    
    Args:
        path: File path to write
        content: Content to write
        encoding: File encoding
        mode: File permissions (octal)
    
    Returns:
        True if file was written successfully
    """
    try:
        path_obj = Path(path)
        
        # Ensure directory exists
        ensure_directory(path_obj.parent)
        
        # Write file
        with open(path_obj, 'w', encoding=encoding) as f:
            f.write(content)
        
        # Set permissions
        os.chmod(path_obj, mode)
        
        logger.debug(f"File written: {path_obj}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to write file {path}: {e}")
        return False


def make_executable(path: Union[str, Path]) -> bool:
    """Make file executable.
    
    Args:
        path: File path to make executable
    
    Returns:
        True if file was made executable successfully
    """
    try:
        path_obj = Path(path)
        
        if not path_obj.exists():
            logger.error(f"File does not exist: {path_obj}")
            return False
        
        # Get current permissions and add execute bit
        current_mode = path_obj.stat().st_mode
        new_mode = current_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH
        
        os.chmod(path_obj, new_mode)
        
        logger.debug(f"Made executable: {path_obj}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to make file executable {path}: {e}")
        return False


def remove_file(path: Union[str, Path]) -> bool:
    """Remove file with error handling.
    
    Args:
        path: File path to remove
    
    Returns:
        True if file was removed successfully or didn't exist
    """
    try:
        path_obj = Path(path)
        
        if path_obj.exists():
            path_obj.unlink()
            logger.debug(f"File removed: {path_obj}")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to remove file {path}: {e}")
        return False


def remove_directory(path: Union[str, Path], recursive: bool = False) -> bool:
    """Remove directory with error handling.
    
    Args:
        path: Directory path to remove
        recursive: Whether to remove directory recursively
    
    Returns:
        True if directory was removed successfully or didn't exist
    """
    try:
        path_obj = Path(path)
        
        if not path_obj.exists():
            return True
        
        if not path_obj.is_dir():
            logger.error(f"Path is not a directory: {path_obj}")
            return False
        
        if recursive:
            shutil.rmtree(path_obj)
        else:
            path_obj.rmdir()
        
        logger.debug(f"Directory removed: {path_obj}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to remove directory {path}: {e}")
        return False


def create_symlink(src: Union[str, Path], dst: Union[str, Path]) -> bool:
    """Create symbolic link with error handling.
    
    Args:
        src: Source path (target of the symlink)
        dst: Destination path (location of the symlink)
    
    Returns:
        True if symlink was created successfully
    """
    try:
        src_path = Path(src)
        dst_path = Path(dst)
        
        # Remove existing symlink if it exists
        if dst_path.is_symlink():
            dst_path.unlink()
        
        # Ensure destination directory exists
        ensure_directory(dst_path.parent)
        
        # Create symlink
        dst_path.symlink_to(src_path)
        
        logger.debug(f"Symlink created: {dst_path} -> {src_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create symlink {dst} -> {src}: {e}")
        return False


def backup_file(path: Union[str, Path], backup_suffix: str = '.bak') -> Optional[Path]:
    """Create backup of file.
    
    Args:
        path: File path to backup
        backup_suffix: Suffix for backup file
    
    Returns:
        Path to backup file if successful, None otherwise
    """
    try:
        path_obj = Path(path)
        
        if not path_obj.exists():
            logger.error(f"File does not exist for backup: {path_obj}")
            return None
        
        backup_path = path_obj.with_suffix(path_obj.suffix + backup_suffix)
        
        # If backup already exists, add timestamp
        if backup_path.exists():
            import time
            timestamp = int(time.time())
            backup_path = path_obj.with_suffix(f"{path_obj.suffix}.{timestamp}{backup_suffix}")
        
        shutil.copy2(path_obj, backup_path)
        
        logger.info(f"Backup created: {backup_path}")
        return backup_path
        
    except Exception as e:
        logger.error(f"Failed to backup file {path}: {e}")
        return None
