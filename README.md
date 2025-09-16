# HamppServer

A simple localhost server manager for **Apache**, **MySQL**, and **PHP** on mobile devices and computers.

![HamppServer](https://github.com/yourchocomate/HamppServer/blob/main/screenshot/Screenshot_20210404-045421_Termux.jpg?raw=true)

## 🌟 What is HamppServer?

HamppServer lets you run a complete web server on your **Android phone** (using Termux) or **Linux computer**. Perfect for:
- 📱 Web development on your phone
- 🎓 Learning PHP, HTML, CSS
- 🧪 Testing websites locally
- 📚 Running phpMyAdmin for database management

## 🚀 Super Easy Installation

### For Android (Termux)
```bash
pkg update && pkg upgrade -y
termux-setup-storage
pkg install git -y
git clone https://github.com/yourchocomate/HamppServer.git
cd HamppServer
chmod +x install
./install
```

### For Ubuntu/Linux
```bash
git clone https://github.com/yourchocomate/HamppServer.git
cd HamppServer
chmod +x install
./install
```

**That's it!** The installer does everything for you.

## 🎮 How to Use

After installation, it's super simple:

```bash
# Just type this command
hampp
```

## ✨ What You Get

- 🌐 **Apache Web Server** - Serves your websites
- 🗄️ **MySQL Database** - Store your app data  
- 🐘 **PHP** - Run dynamic websites
- 📊 **phpMyAdmin** - Manage databases easily
- 📱 **Mobile Friendly** - Works great on phones
- 🎯 **Beginner Friendly** - No complex setup needed

## 🌐 Quick Commands

### Start Your Server
```bash
hampp
# Then choose option 1 to start Apache
```

### Check if Everything is Running
```bash
hampp status
```

### Direct Commands (for advanced users)
```bash
hampp start-apache    # Start web server
hampp start-mysql     # Start database
hampp stop-apache     # Stop web server
hampp stop-mysql      # Stop database
```

## 🎯 Access Your Server

Once Apache is running:
- **Main website**: http://localhost:8080
- **PHP info**: http://localhost:8080/phpinfo.php  
- **Database manager**: http://localhost:8080/phpmyadmin

## 📁 Where to Put Your Files

### On Android (Termux)
Put your website files in: `/sdcard/www/`

### On Linux
Put your website files in: `~/www/`

Just create an `index.html` or `index.php` file and it will show up!

## 🆘 Need Help?

### Common Issues

**"Command not found"**
- Make sure you're in the HamppServer directory
- Try `python` instead of `python3`

**"Permission denied"**
- On Termux: Run `termux-setup-storage` first
- On Linux: Some commands might need `sudo`

**"Port already in use"**
- Another program is using port 8080
- Use: `python3 hampp.py start-apache --port 9090`

**Can't access website**
- Make sure Apache is running: `python3 hampp.py status`
- Check the URL: http://localhost:8080
- Try refreshing your browser

### Getting Help
1. Check if all services are running: `python3 hampp.py status`
2. Look for error messages in the terminal
3. Try restarting: stop and start services again
4. Open an issue on GitHub if problems persist

## 🗑️ Uninstalling HamppServer

If you want to remove HamppServer completely:

```bash
# Run the uninstaller
chmod +x uninstall
./uninstall
```

The uninstaller will:
- ✅ Stop all running services
- ✅ Remove the `hampp` command
- ✅ Remove configuration files
- ✅ Clean up log and temporary files
- ✅ Preserve your web files and databases

## 🔧 Troubleshooting

### Reset Everything
If something goes wrong, you can always start fresh:

```bash
# Stop all services
hampp stop-apache
hampp stop-mysql

# Reset configuration
hampp config-reset

# Start again
hampp
```

## 🎓 Learning Resources

### For Beginners
- **HTML/CSS**: Start with simple HTML files in your www folder
- **PHP**: Try the phpinfo page first, then create simple PHP scripts
- **MySQL**: Use phpMyAdmin to create databases and tables

### Example Files
Create these files in your www folder to get started:

**hello.html**
```html
<!DOCTYPE html>
<html>
<head><title>My First Page</title></head>
<body><h1>Hello World!</h1></body>
</html>
```

**test.php**
```php
<?php 
echo "PHP is working! Today is " . date('Y-m-d');
?>
```

## 👨‍💻 Contact & Support

**Created by Md Habibur Rahman**

📧 **Email**: [yourchocomate@gmail.com](mailto:yourchocomate@gmail.com)  
📘 **Facebook**: [yourchocomate](https://facebook.com/yourchocomate)

### Found a Bug?
Open an issue on GitHub and I'll help you fix it!

### Want to Say Thanks?
Give this project a ⭐ star on GitHub!

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

<div align="center">
  <strong>🚀 Happy coding with HamppServer! 🚀</strong>
  <br><br>
  <em>Made with ❤️ for mobile developers and beginners</em>
</div>