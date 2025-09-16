#!/usr/bin/env python3
"""
Quick test to verify Apache MPM and configuration fixes
"""

import os
import subprocess

def test_apache_mpm():
    """Test that MPM modules are available and can be loaded."""
    print("🔧 Testing Apache MPM modules...")
    
    modules_dir = "/data/data/com.termux/files/usr/libexec/apache2"
    mpm_modules = ["mod_mpm_prefork.so", "mod_mpm_worker.so"]
    
    found_mpm = []
    for mpm in mpm_modules:
        path = f"{modules_dir}/{mpm}"
        if os.path.exists(path):
            found_mpm.append(mpm)
            print(f"  ✅ {mpm}")
        else:
            print(f"  ❌ {mpm} missing")
    
    if found_mpm:
        print(f"✅ Found {len(found_mpm)} MPM module(s) - Apache should start")
        return True
    else:
        print("❌ No MPM modules found - Apache will fail")
        return False

def test_apache_config():
    """Test Apache configuration generation."""
    print("\n⚙️ Testing Apache configuration...")
    
    try:
        httpd_bin = "/data/data/com.termux/files/usr/bin/httpd"
        if not os.path.exists(httpd_bin):
            print(f"❌ Apache binary not found: {httpd_bin}")
            return False
        
        # Test configuration syntax
        result = subprocess.run([httpd_bin, "-t"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Apache configuration test passed")
            return True
        else:
            print(f"❌ Apache configuration test failed:")
            print(f"   {result.stderr.strip()}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Apache config: {e}")
        return False

def main():
    """Run MPM and configuration tests."""
    print("🧪 Apache MPM Configuration Test")
    print("=" * 40)
    
    tests_passed = 0
    total_tests = 2
    
    if test_apache_mpm():
        tests_passed += 1
    
    if test_apache_config():
        tests_passed += 1
    
    print("\n" + "=" * 40)
    print(f"📊 Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 Apache should start successfully!")
        print("\n💡 Try: python3 hampp.py interactive")
    else:
        print("⚠️ Issues detected. Check output above.")
        print("\n💡 Try: python3 check_termux_modules.py")

if __name__ == "__main__":
    main()