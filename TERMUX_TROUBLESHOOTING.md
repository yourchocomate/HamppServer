# Termux Troubleshooting Guide

This guide helps fix common issues when running HamppServer on Termux (Android).

## 🔧 Common Apache Issues

### Issue: "Cannot load libphp.so"
```
httpd: Syntax error on line 9 of /data/data/com.termux/files/usr/etc/apache2/httpd.conf: 
Cannot load libexec/apache2/libphp.so into server: dlopen failed: library not found
```

**Solution:**
```bash
# Reinstall PHP-Apache module
pkg uninstall php-apache
pkg install php-apache

# Check if PHP module exists
ls -la /data/data/com.termux/files/usr/lib/apache2/modules/libphp.so

# If not found, try alternative location
ls -la /data/data/com.termux/files/usr/libexec/apache2/libphp.so
```

### Issue: Apache shows usage help instead of starting
```
Usage: /data/data/com.termux/files/usr/bin/httpd [-D name] [-d directory] [-f file]...
```

**Solution:** 
This is fixed in HamppServer v2.0! The new version uses the correct `httpd -D FOREGROUND` command for Termux.

**Manual fix:**
```bash
# Start Apache manually
/data/data/com.termux/files/usr/bin/httpd -D FOREGROUND &

# Or test the configuration first
/data/data/com.termux/files/usr/bin/httpd -t
```

### Issue: Apache won't start with module errors

**Solution:**
```bash
# Check Apache modules directory
ls -la /data/data/com.termux/files/usr/lib/apache2/modules/

# Verify Apache installation
pkg reinstall apache2

# Test Apache configuration
/data/data/com.termux/files/usr/bin/httpd -t
```

## 🗄️ Common MySQL Issues

### Issue: "No such file or directory: mysql.server"
```
ERROR: Error starting MySQL: [Errno 2] No such file or directory: 
'/data/data/com.termux/files/usr/bin/mysql.server'
```

**Solution:** 
This is fixed in HamppServer v2.0! The new version automatically detects available MySQL/MariaDB binaries.

**Manual fix:**
```bash
# Check available MySQL/MariaDB binaries
ls -la /data/data/com.termux/files/usr/bin/ | grep -i mysql
ls -la /data/data/com.termux/files/usr/bin/ | grep -i maria

# Usually MariaDB is installed, not MySQL
which mariadbd
which mysqld_safe

# Start MariaDB manually (without --user option in Termux)
mariadbd --datadir=/data/data/com.termux/files/usr/var/lib/mysql &
```

### Issue: "One can only use the --user switch if running as root"
```
/data/data/com.termux/files/usr/bin/mariadbd: One can only use the --user switch if running as root
```

**Solution:**
This is fixed in HamppServer v2.0! The new version removes the `--user` option for Termux.

**Manual fix:**
```bash
# Start without --user option
mariadbd --datadir=/data/data/com.termux/files/usr/var/lib/mysql &

# Or use mysqld_safe
mysqld_safe &
```

### Issue: "unknown option '--daemonize'"
```
/data/data/com.termux/files/usr/bin/mariadbd: unknown option '--daemonize'
```

**Solution:**
This is fixed in HamppServer v2.0! The new version removes the `--daemonize` option for Termux.

**Manual fix:**
```bash
# Start in background without --daemonize
mariadbd --datadir=/data/data/com.termux/files/usr/var/lib/mysql &
```

### Issue: MySQL data directory not initialized

**Solution:**
```bash
# Initialize MySQL data directory
mysql_install_db --user=mysql --datadir=/data/data/com.termux/files/usr/var/lib/mysql

# Set proper permissions
chmod 755 /data/data/com.termux/files/usr/var/lib/mysql
```

## 📱 Storage Permission Issues

### Issue: Cannot create /sdcard/www directory

**Solution:**
```bash
# Grant storage permission to Termux
termux-setup-storage

# Wait for permission dialog and accept

# Verify access
ls -la /sdcard/

# Create www directory manually if needed
mkdir -p /sdcard/www
```

## 🐍 Python Dependencies Issues

### Issue: "ModuleNotFoundError" for HamppServer modules

**Solution:**
```bash
# Install missing Python packages
pip install click rich pyyaml jinja2 psutil requests

# If pip fails, update it first
pip install --upgrade pip

# Alternative: use pkg to install Python packages
pkg install python-cryptography python-lxml
```

## 🔍 Debugging Commands

### Check Services Status
```bash
# Check if Apache is running
ps aux | grep httpd

# Check if MySQL is running  
ps aux | grep mysql
ps aux | grep maria

# Check listening ports
netstat -tlnp | grep :8080
netstat -tlnp | grep :3306
```

### Check File Permissions
```bash
# Check Apache config file
ls -la /data/data/com.termux/files/usr/etc/apache2/httpd.conf

# Check document root permissions
ls -la /sdcard/www/

# Check MySQL data directory
ls -la /data/data/com.termux/files/usr/var/lib/mysql/
```

### Test Components Individually
```bash
# Test Apache configuration
/data/data/com.termux/files/usr/bin/httpd -t

# Test PHP
php -v
php -m | grep -i apache

# Test MySQL connection
mysql -u root
```

## 🛠️ Manual Service Management

### Start Apache Manually
```bash
# Method 1: Using httpd directly
/data/data/com.termux/files/usr/bin/httpd -D FOREGROUND

# Method 2: Using apachectl (if available)
/data/data/com.termux/files/usr/bin/apachectl start
```

### Start MySQL Manually
```bash
# Method 1: Using mariadbd
mariadbd --user=mysql --datadir=/data/data/com.termux/files/usr/var/lib/mysql &

# Method 2: Using mysqld_safe
mysqld_safe --user=mysql &

# Method 3: Using systemctl-style command
mysql.server start
```

## 📋 Complete Reinstallation

If nothing works, try a complete reinstallation:

```bash
# Stop HamppServer
python3 hampp.py stop-apache
python3 hampp.py stop-mysql

# Uninstall packages
pkg uninstall apache2 mariadb php php-apache

# Clear cache
pkg clean

# Update package list
pkg update

# Reinstall everything
pkg install apache2 mariadb php php-apache

# Reinstall HamppServer
cd HamppServer
./install
```

## 🚨 Emergency Reset

If the system is completely broken:

```bash
# Reset Termux completely (⚠️ THIS WILL DELETE ALL DATA)
# Only do this as a last resort!

# Exit Termux
exit

# In Android, go to Settings > Apps > Termux > Storage > Clear Data
# Then reinstall Termux from Play Store/F-Droid

# Restore HamppServer
pkg update
pkg install git
git clone https://github.com/yourchocomate/HamppServer.git
cd HamppServer
./install
```

## 💡 Tips for Better Performance

1. **Use /sdcard for web files** - faster than internal storage
2. **Keep Termux updated** - `pkg upgrade` regularly
3. **Monitor memory usage** - Android may kill background processes
4. **Use wake locks** - install Termux:Boot to keep services running
5. **Close other apps** - free up RAM for better performance

## 📞 Getting Help

If you're still having issues:

1. **Check logs**: Look at the actual error messages
2. **Share error details**: Include the full error output
3. **Mention your setup**: Android version, Termux version, etc.
4. **Open an issue**: https://github.com/yourchocomate/HamppServer/issues

Remember: Termux is a complex environment, and some issues may be related to Android limitations rather than HamppServer itself.
