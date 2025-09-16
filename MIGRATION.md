# Migration Guide: HamppServer v1.x to v2.0

This guide helps you migrate from the legacy HamppServer (v1.x) to the completely refactored HamppServer v2.0.

## 🔄 What Changed

### Major Changes
- **Complete rewrite** in modern Python with proper architecture
- **New command-line interface** using Click framework
- **Configuration management** with YAML files
- **Improved error handling** and logging
- **Cross-platform support** beyond just Termux
- **Package structure** for better maintainability

### Breaking Changes
- ❌ Old `hampp` script location changed
- ❌ Configuration format changed from hardcoded to YAML
- ❌ Some command flags and options renamed
- ❌ Installation process simplified but different

## 📦 Installation Migration

### Old Installation (v1.x)
```bash
git clone https://github.com/yourchocomate/HamppServer.git
cd HamppServer
chmod +x install
./install
```

### New Installation (v2.0)
```bash
git clone https://github.com/yourchocomate/HamppServer.git
cd HamppServer
chmod +x install
./install
```

## 🔧 Command Migration

### Starting Apache Server

#### Old (v1.x)
```bash
hampp  # Interactive menu, choose option 1
```

#### New (v2.0)
```bash
# Interactive mode (recommended for beginners)
python3 hampp.py interactive

# Direct commands (for advanced users)
python3 hampp.py start-apache
python3 hampp.py start-apache --port 9090
```

### Starting MySQL Server

#### Old (v1.x)
```bash
hampp  # Interactive menu, choose option 3
```

#### New (v2.0)
```bash
python3 hampp.py start-mysql
```

### Stopping Services

#### Old (v1.x)
```bash
hampp  # Interactive menu, choose option 2 or 4
```

#### New (v2.0)
```bash
python3 hampp.py stop-apache
python3 hampp.py stop-mysql

# Or restart
python3 hampp.py restart apache
python3 hampp.py restart mysql
```

### Checking Status

#### Old (v1.x)
- No direct status command
- Had to manually check if services were running

#### New (v2.0)
```bash
python3 hampp.py status  # Shows comprehensive status of all services
```

## ⚙️ Configuration Migration

### Old Configuration (v1.x)
- Hardcoded paths in Python files
- Port and directory settings via prompts
- No persistent configuration

### New Configuration (v2.0)
Configuration is now stored in YAML files:

**Location**: `~/.config/hampp/config.yaml` (Linux) or `/data/data/com.termux/files/home/.config/hampp/config.yaml` (Termux)

```yaml
server:
  apache_port: 8080
  mysql_port: 3306
  document_root: "/sdcard/www"  # or your preferred path
  php_version: "auto"
  enable_phpmyadmin: true
  auto_start_services: false
```

#### Managing Configuration
```bash
# View current configuration
hampp config-show

# Set specific values
hampp config-set apache_port 9090
hampp config-set document_root "/custom/www"

# Reset to defaults
hampp config-reset
```

## 📁 File Structure Migration

### Old Structure (v1.x)
```
HamppServer/
├── .HamppServer.py           # Main script
├── .setup.aex               # Setup script
├── install                  # Installation script
├── core/
│   ├── hampp               # Command wrapper
│   ├── index.php           # Default page
│   └── phpinfo.php         # PHP info page
```

### New Structure (v2.0)
```
hampp-server/
├── hampp/                   # Python package
│   ├── core/               # Core functionality
│   ├── cli/                # CLI interface
│   ├── templates/          # Configuration templates
│   └── utils/              # Utility modules
├── assets/                 # Web assets
├── tests/                  # Test suite
├── pyproject.toml          # Package configuration
└── requirements.txt        # Dependencies
```

## 🔄 Data Migration

### Document Root Files
Your existing web files should continue to work without changes:
- `index.php` or `index.html` files
- PHPMyAdmin installation
- Any custom web applications

The new version will detect and use your existing document root, or you can configure a new one.

### Backing Up Your Data
Before migrating, backup your important files:

```bash
# Backup web files
cp -r /sdcard/www ~/backup_www  # Termux
cp -r ~/www ~/backup_www        # Linux

# Backup any custom configurations
# (Note: v1.x didn't have persistent config files)
```

## 🚀 Step-by-Step Migration

### 1. Backup Current Setup
```bash
# Stop any running services
# In old hampp: choose stop options

# Backup web files
cp -r /sdcard/www ~/hampp_backup
```

### 2. Remove Old Installation
```bash
# Remove old hampp command
rm -f /data/data/com.termux/files/usr/bin/hampp  # Termux
sudo rm -f /usr/local/bin/hampp                  # Linux

# Remove old files (optional, but recommended)
rm -rf ~/HamppServer  # or wherever you had it installed
```

### 3. Remove Old Installation (Optional)
```bash
# If you want to completely remove the old version
cd /path/to/old/HamppServer
chmod +x uninstall
./uninstall
```

### 4. Install New Version
```bash
git clone https://github.com/yourchocomate/HamppServer.git
cd HamppServer
chmod +x install
./install
```

### 5. Configure (Optional)
```bash
# Set your preferred settings
python3 hampp.py config-set document_root "/sdcard/www"  # or your path
python3 hampp.py config-set apache_port 8080             # or your preferred port
```

### 6. Test Installation
```bash
# Check status
python3 hampp.py status

# Start services
python3 hampp.py start-apache
python3 hampp.py start-mysql

# Verify everything works
# Visit http://localhost:8080 in your browser
```

## 🆘 Troubleshooting

### Common Issues

#### "Command not found: hampp"
```bash
# Make sure package is installed
pip install -e .

# Check if ~/.local/bin is in PATH
echo $PATH

# Add to PATH if needed (in ~/.bashrc or ~/.zshrc)
export PATH="$HOME/.local/bin:$PATH"
```

#### "Permission denied" errors
```bash
# Make sure directories exist and have proper permissions
hampp config-show  # Check configured paths
ls -la /sdcard/www  # Verify directory permissions
```

#### Services won't start
```bash
# Check detailed logs
hampp status -v  # Verbose output

# Check if ports are available
netstat -tulpn | grep :8080
netstat -tulpn | grep :3306
```

#### Configuration issues
```bash
# Reset to defaults and reconfigure
hampp config-reset
hampp config-set document_root "/your/preferred/path"
```

## 🆕 New Features You Can Use

### 1. Status Monitoring
```bash
hampp status  # Real-time service status with resource usage
```

### 2. Better Error Messages
The new version provides clear, actionable error messages instead of cryptic failures.

### 3. Configuration Management
```bash
# Persistent settings
hampp config-set enable_phpmyadmin false
hampp config-set auto_start_services true
```

### 4. Interactive Mode
```bash
hampp interactive  # Guided menu system (similar to old behavior)
```

### 5. Improved Web Interface
Visit your server to see the new, modern web interface with:
- Responsive design
- Better navigation
- Enhanced PHP info page
- Quick access links

## 📞 Getting Help

If you encounter issues during migration:

1. **Check the logs**: Use `hampp status -v` for verbose output
2. **Reset configuration**: Use `hampp config-reset` to start fresh
3. **Reinstall dependencies**: Use `hampp install --force`
4. **Read documentation**: Check `hampp --help` or the README
5. **Report issues**: Open an issue on GitHub with detailed error messages

## 🎉 Welcome to HamppServer v2.0!

The new version provides much better reliability, error handling, and user experience while maintaining the simplicity that made the original popular. Take some time to explore the new features and improved workflows!
