#!/usr/bin/env python3
"""
Check what Apache modules and PHP modules are available in Termux
"""

import os
import subprocess
import sys
from pathlib import Path

def check_apache_modules():
    """Check available Apache modules in Termux."""
    print("🔍 Checking Apache modules...")
    
    prefix = "/data/data/com.termux/files/usr"
    modules_dir = f"{prefix}/libexec/apache2"  # Correct path for Termux
    
    if not os.path.exists(modules_dir):
        print(f"❌ Apache modules directory not found: {modules_dir}")
        return
    
    print(f"✅ Apache modules directory: {modules_dir}")
    
    # List all available modules
    try:
        modules = os.listdir(modules_dir)
        print(f"📋 Found {len(modules)} modules:")
        for module in sorted(modules):
            if module.endswith('.so'):
                print(f"  ✅ {module}")
    except Exception as e:
        print(f"❌ Error listing modules: {e}")

def check_php_modules():
    """Check available PHP modules for Apache."""
    print("\n🐘 Checking PHP modules...")
    
    prefix = "/data/data/com.termux/files/usr"
    php_locations = [
        f"{prefix}/libexec/apache2/libphp.so",
        f"{prefix}/libexec/apache2/libphp8.so", 
        f"{prefix}/libexec/apache2/libphp7.so",
    ]
    
    found_php = False
    for location in php_locations:
        if os.path.exists(location):
            print(f"✅ PHP module found: {location}")
            found_php = True
        else:
            print(f"❌ PHP module not found: {location}")
    
    if not found_php:
        print("⚠️ No PHP modules found for Apache")

def check_apache_config():
    """Check Apache configuration."""
    print("\n⚙️ Checking Apache configuration...")
    
    prefix = "/data/data/com.termux/files/usr"
    config_file = f"{prefix}/etc/apache2/httpd.conf"
    
    if os.path.exists(config_file):
        print(f"✅ Apache config found: {config_file}")
        
        # Test the configuration
        try:
            result = subprocess.run([f"{prefix}/bin/httpd", "-t"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("✅ Apache configuration test passed")
            else:
                print(f"❌ Apache configuration test failed:")
                print(f"   {result.stderr}")
        except Exception as e:
            print(f"❌ Error testing Apache config: {e}")
    else:
        print(f"❌ Apache config not found: {config_file}")

def check_mysql_binaries():
    """Check available MySQL/MariaDB binaries."""
    print("\n🗄️ Checking MySQL/MariaDB binaries...")
    
    prefix = "/data/data/com.termux/files/usr"
    binaries = [
        f"{prefix}/bin/mariadbd",
        f"{prefix}/bin/mysqld",
        f"{prefix}/bin/mysqld_safe",
        f"{prefix}/bin/mysql",
        f"{prefix}/bin/mysql_install_db",
    ]
    
    for binary in binaries:
        if os.path.exists(binary):
            print(f"✅ Found: {binary}")
            # Try to get version
            try:
                result = subprocess.run([binary, "--version"], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    version = result.stdout.strip()[:100]  # Limit output
                    print(f"   Version: {version}")
            except Exception:
                pass
        else:
            print(f"❌ Not found: {binary}")

def check_data_directories():
    """Check required data directories."""
    print("\n📁 Checking data directories...")
    
    directories = [
        "/sdcard/www",
        "/data/data/com.termux/files/usr/var/lib/mysql",
        "/data/data/com.termux/files/usr/var/log/apache2",
        "/data/data/com.termux/files/usr/var/run/apache2",
    ]
    
    for directory in directories:
        if os.path.exists(directory):
            print(f"✅ Directory exists: {directory}")
            # Check permissions
            if os.access(directory, os.W_OK):
                print(f"   ✅ Writable")
            else:
                print(f"   ⚠️ Not writable")
        else:
            print(f"❌ Directory missing: {directory}")
            # Try to create
            try:
                os.makedirs(directory, exist_ok=True)
                print(f"   ✅ Created directory")
            except Exception as e:
                print(f"   ❌ Cannot create: {e}")

def check_processes():
    """Check running processes."""
    print("\n🔄 Checking running processes...")
    
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True, timeout=10)
        lines = result.stdout.split('\n')
        
        apache_processes = [line for line in lines if 'httpd' in line.lower()]
        mysql_processes = [line for line in lines if 'maria' in line.lower() or 'mysql' in line.lower()]
        
        print(f"📊 Apache processes: {len(apache_processes)}")
        for proc in apache_processes:
            print(f"   {proc}")
        
        print(f"📊 MySQL processes: {len(mysql_processes)}")
        for proc in mysql_processes:
            print(f"   {proc}")
            
    except Exception as e:
        print(f"❌ Error checking processes: {e}")

def main():
    """Run all checks."""
    print("🔍 Termux Apache/MySQL Module Checker")
    print("=" * 50)
    
    # Check if we're on Termux
    if not os.path.exists("/data/data/com.termux"):
        print("⚠️ This script is designed for Termux")
        print("ℹ️ Running anyway for testing...")
    
    check_apache_modules()
    check_php_modules()
    check_apache_config()
    check_mysql_binaries()
    check_data_directories()
    check_processes()
    
    print("\n" + "=" * 50)
    print("🎯 Recommendations:")
    print("1. If PHP modules are missing: pkg install php-apache")
    print("2. If Apache modules are missing: pkg reinstall apache2")
    print("3. If MySQL is missing: pkg install mariadb")
    print("4. Check the HamppServer logs for specific errors")
    
    print("\n💡 Next steps:")
    print("  python3 hampp.py interactive")
    print("  # Try starting services and check for specific error messages")

if __name__ == '__main__':
    main()
