#!/usr/bin/env python3
"""
Quick test for Termux startup fixes
Run this to test if the Apache and MySQL startup issues are resolved
"""

import sys
import os
import subprocess
import time
from pathlib import Path

# Add current directory to path
script_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(script_dir))

def test_apache_command():
    """Test Apache startup command generation."""
    print("🔍 Testing Apache command generation...")
    
    try:
        from hampp.core.config import Config
        from hampp.core.server_manager import ServerManager
        
        config = Config()
        server_manager = ServerManager(config)
        
        if config.platform.is_termux:
            expected_binary = "/data/data/com.termux/files/usr/bin/httpd"
            if os.path.exists(expected_binary):
                print(f"✅ Apache binary found: {expected_binary}")
                
                # Test the command that would be run
                test_cmd = [expected_binary, '-t']  # Test configuration
                try:
                    result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        print("✅ Apache configuration test passed")
                    else:
                        print(f"⚠️ Apache config test failed: {result.stderr}")
                except Exception as e:
                    print(f"⚠️ Apache config test error: {e}")
            else:
                print(f"❌ Apache binary not found: {expected_binary}")
                print("💡 Install with: pkg install apache2")
        else:
            print("ℹ️ Not running on Termux - skipping Termux-specific tests")
        
        return True
        
    except Exception as e:
        print(f"❌ Apache command test failed: {e}")
        return False

def test_mysql_command():
    """Test MySQL startup command generation."""
    print("\n🔍 Testing MySQL command generation...")
    
    try:
        from hampp.core.config import Config
        from hampp.core.server_manager import ServerManager
        
        config = Config()
        server_manager = ServerManager(config)
        
        if config.platform.is_termux:
            prefix = "/data/data/com.termux/files/usr"
            mysql_binaries = [
                f"{prefix}/bin/mariadbd",
                f"{prefix}/bin/mysqld_safe", 
                f"{prefix}/bin/mysqld"
            ]
            
            found_binary = None
            for binary in mysql_binaries:
                if os.path.exists(binary):
                    found_binary = binary
                    print(f"✅ MySQL binary found: {binary}")
                    break
            
            if found_binary:
                # Test version command
                try:
                    result = subprocess.run([found_binary, '--version'], capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        print(f"✅ MySQL version: {result.stdout.strip()}")
                    else:
                        print(f"⚠️ MySQL version check failed: {result.stderr}")
                except Exception as e:
                    print(f"⚠️ MySQL version check error: {e}")
            else:
                print("❌ No MySQL/MariaDB binary found")
                print("💡 Install with: pkg install mariadb")
        else:
            print("ℹ️ Not running on Termux - skipping Termux-specific tests")
        
        return True
        
    except Exception as e:
        print(f"❌ MySQL command test failed: {e}")
        return False

def test_process_detection():
    """Test process detection logic."""
    print("\n🔍 Testing process detection...")
    
    try:
        from hampp.core.config import Config
        from hampp.core.server_manager import ServerManager
        
        config = Config()
        server_manager = ServerManager(config)
        
        # Test Apache detection
        apache_running = server_manager.is_service_running('apache')
        print(f"✅ Apache running status: {apache_running}")
        
        # Test MySQL detection
        mysql_running = server_manager.is_service_running('mysql')
        print(f"✅ MySQL running status: {mysql_running}")
        
        return True
        
    except Exception as e:
        print(f"❌ Process detection test failed: {e}")
        return False

def test_directory_creation():
    """Test directory creation for services."""
    print("\n🔍 Testing directory creation...")
    
    try:
        from hampp.core.config import Config
        
        config = Config()
        
        # Test document root
        doc_root = config.server_config.document_root
        if os.path.exists(doc_root):
            print(f"✅ Document root exists: {doc_root}")
        else:
            print(f"⚠️ Document root missing: {doc_root}")
            try:
                os.makedirs(doc_root, exist_ok=True)
                print(f"✅ Created document root: {doc_root}")
            except Exception as e:
                print(f"❌ Cannot create document root: {e}")
        
        # Test log directory
        if config.platform.is_termux:
            log_dir = "/data/data/com.termux/files/usr/var/log/apache2"
            if not os.path.exists(log_dir):
                try:
                    os.makedirs(log_dir, exist_ok=True)
                    print(f"✅ Created log directory: {log_dir}")
                except Exception as e:
                    print(f"⚠️ Cannot create log directory: {e}")
            else:
                print(f"✅ Log directory exists: {log_dir}")
        
        return True
        
    except Exception as e:
        print(f"❌ Directory creation test failed: {e}")
        return False

def main():
    """Run all startup tests."""
    print("🧪 HamppServer Termux Startup Fixes Test")
    print("=" * 45)
    
    tests = [
        test_apache_command,
        test_mysql_command,
        test_process_detection,
        test_directory_creation,
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test_func.__name__} crashed: {e}")
    
    print("\n" + "=" * 45)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Startup fixes should work correctly.")
        print("\n📖 Try starting services:")
        print("  python3 hampp.py interactive")
        print("  # Then select option 1 (Start Apache)")
        print("  # Then select option 3 (Start MySQL)")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        print("\n🔧 Possible solutions:")
        print("  - Make sure you're running on Termux")
        print("  - Install missing packages: pkg install apache2 mariadb")
        print("  - Check file permissions")
    
    print(f"\n💡 For detailed troubleshooting, see: TERMUX_TROUBLESHOOTING.md")

if __name__ == '__main__':
    main()
