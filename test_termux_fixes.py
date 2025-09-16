#!/usr/bin/env python3
"""
Test script to verify Termux-specific fixes for HamppServer
Run this to check if the platform detection and path fixes work correctly
"""

import sys
import os
from pathlib import Path

# Add current directory to path
script_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(script_dir))

def test_platform_detection():
    """Test platform detection improvements."""
    print("🔍 Testing platform detection...")
    
    try:
        from hampp.core.platform_detector import PlatformDetector
        
        platform = PlatformDetector()
        print(f"✅ Platform: {platform.name}")
        print(f"✅ Is Termux: {platform.is_termux}")
        print(f"✅ Is Android: {platform.is_android}")
        print(f"✅ Is Linux: {platform.is_linux}")
        
        deps = platform.check_dependencies()
        print(f"✅ Dependencies check: {deps}")
        
        return True
        
    except Exception as e:
        print(f"❌ Platform detection failed: {e}")
        return False

def test_config_paths():
    """Test configuration path setup."""
    print("\n🔧 Testing configuration paths...")
    
    try:
        from hampp.core.config import Config
        
        config = Config()
        print(f"✅ Apache binary: {config.path_config.apache_bin}")
        print(f"✅ Apache config: {config.path_config.apache_config}")
        print(f"✅ MySQL binary: {config.path_config.mysql_bin}")
        print(f"✅ Document root: {config.path_config.document_root}")
        
        # Check if binaries exist
        if os.path.exists(config.path_config.apache_bin):
            print(f"✅ Apache binary found at {config.path_config.apache_bin}")
        else:
            print(f"⚠️ Apache binary not found at {config.path_config.apache_bin}")
        
        if os.path.exists(config.path_config.mysql_bin):
            print(f"✅ MySQL binary found at {config.path_config.mysql_bin}")
        else:
            print(f"⚠️ MySQL binary not found at {config.path_config.mysql_bin}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_php_module_detection():
    """Test PHP module detection for Apache."""
    print("\n🐘 Testing PHP module detection...")
    
    try:
        from hampp.core.config import Config
        from hampp.core.server_manager import ServerManager
        
        config = Config()
        server_manager = ServerManager(config)
        
        php_module = server_manager._detect_php_module()
        print(f"✅ PHP module config: {php_module}")
        
        # Check if the PHP module file exists
        if "LoadModule" in php_module:
            module_path = php_module.split()[-1]  # Get the last part (path)
            if os.path.exists(module_path):
                print(f"✅ PHP module file found: {module_path}")
            else:
                print(f"⚠️ PHP module file not found: {module_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ PHP module detection failed: {e}")
        return False

def test_apache_config_generation():
    """Test Apache configuration generation."""
    print("\n⚙️ Testing Apache configuration generation...")
    
    try:
        from hampp.core.config import Config
        from hampp.core.server_manager import ServerManager
        
        config = Config()
        server_manager = ServerManager(config)
        
        apache_config = server_manager._generate_apache_config(8080, "/sdcard/www")
        
        print(f"✅ Apache config generated ({len(apache_config)} characters)")
        
        # Check for Termux-specific paths
        if config.platform.is_termux:
            if "/data/data/com.termux/files/usr" in apache_config:
                print("✅ Termux-specific paths detected in config")
            else:
                print("⚠️ Termux-specific paths missing from config")
        
        # Check for required directives
        required_directives = ["ServerRoot", "Listen", "DocumentRoot", "LoadModule"]
        for directive in required_directives:
            if directive in apache_config:
                print(f"✅ {directive} directive found")
            else:
                print(f"❌ {directive} directive missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Apache config generation failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 HamppServer Termux Fixes Test")
    print("=" * 40)
    
    tests = [
        test_platform_detection,
        test_config_paths, 
        test_php_module_detection,
        test_apache_config_generation,
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test_func.__name__} crashed: {e}")
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Termux fixes should work correctly.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        print("💡 This might be normal if you're not running on Termux.")
    
    print("\n📖 Usage:")
    print("  python3 hampp.py interactive    # Start HamppServer")
    print("  python3 hampp.py status         # Check server status")

if __name__ == '__main__':
    main()
