# Tool Name :- HamppServer
# Author :- Md Habibur Rahman
# Date :- 03 April 2021

import sys,os,os.path,random,time
from os import path
from colorama import *
from colorama import Fore,Back,init
from platform import system
from time import sleep
import requests
import getpass
init()
os.system("clear")
spath = "/data/data/com.termux/files/usr/share/"
epath = "/data/data/com.termux/files/usr/etc/"
def logo():
        clear = "\x1b[0m"
        colors = [36, 32, 34, 35, 31, 37  ]

        x = """ 


   __ __                       ____                    
  / // /__ ___ _  ___  ___    / __/__ _____  _____ ____
 / _  / _ `/  ' \/ _ \/ _ \  _\ \/ -_) __/ |/ / -_) __/
/_//_/\_,_/_/_/_/ .__/ .__/ /___/\__/_/  |___/\__/_/   
               /_/  /_/                                

             
 Author: Md Habibur Rahman
 Facebook: https://facebook.com/yourchocomate

 1) Start Php Apache Server
 2) Stop Php Apache Server
 3) Start Mysql Server
 4) Stop Mysql Server
 5) Exit
             	  		  
			                  """
        for N, line in enumerate(x.split("\n")):
            sys.stdout.write("\x1b[1;%dm%s%s\n" % (random.choice(colors), line, clear))
            sleep(0.05)


logo()

def Main():
	
	choice= input('\n Choose Number => ')
	
	if choice=='1':
	   
	   if system() == 'Linux':
	    print("\n \033[01;32mWant to set custom port and web directory?")
	    port_c = input("\n \033[01;32mType \033[01;33m'y' \033[01;32mfor yes & \033[01;33m'n' \033[01;32mfor continue with default port \033[01;33m'8080' \033[01;32mand default web directory \033[01;33m'/sdcard/www' \033[01;32m=>")
	    if port_c == "y":
	    	c_port = input('Set port =>')
	    	if len(c_port) == 4:
	    		if (path.exists(spath+'HamppServer/core/hampp.conf')):
		    		file = open(spath+"HamppServer/core/hampp.conf", "r")
		    		output = file.read().replace('{{HamppPort}}', c_port)
		    		if(output):
		    			set_dir = input("\n \033[01;32mSet custom web directory- default is \033[01;33m/sdcard/www \033[01;32m=>")
		    			if len(set_dir) != 0 and path.exists(set_dir):
		    				final = output.replace('{{HamppDir}}', set_dir)
		    				
		    				#httpd.conf file replacing
		    				con_file = open(epath+'apache2/httpd.conf', 'w')
		    				con_file.write(final)
		    				file.close()
		    				con_file.close()
		    				
		    				#Start Apache server
		    				os.system('apachectl start')
		    				url = "http://127.0.0.1:"+c_port
		    				request = requests.get(url)
		    				if "Apache" in request.headers['server']:
		    					print ('''\n\n''')
		    					print ('''\033[1;32m Apache Server Started Succesfully at\033[1;33m''',url,'''\033[1;32mshowing files from\033[1;33m''',set_dir,'''\033[1;32m ..........\033[1;33m\ \033[00m \n\n''')
		    					sleep(0.1)
		    				else:
		    					print("\n \033[1;31mApache Starting Failed")
		    				Main()
		    			elif len(set_dir) == 0:
		    				final = output.replace('{{HamppDir}}', '/sdcard/www')
		    				
		    				#httpd.conf file replacing
		    				con_file = open(epath+'apache2/httpd.conf', 'wt')
		    				con_file.seek(0)
		    				con_file.write(final)
		    				con_file.truncate()
		    				
		    				#Start Apache server
		    				os.system('apachectl start')
		    				url = "http://127.0.0.1:"+c_port
		    				request = requests.get(url)
		    				if "Apache" in request.headers['server']:
		    					print ('''\n\n''')
		    					print ('''\033[1;32m Apache Server Started Succesfully at\033[1;33m''',url,'''\033[1;32mshowing files from \033[1;33m'/sdcard/www'\033[1;32m ..........\033[1;33m\ \033[00m \n\n''')
		    					sleep(0.1)
		    				else:
		    					print("\n \033[1;31mApache Starting Failed")
		    				Main()
		    			else:
		    				print("\n \033[1;31mPlease Specify A Valid Directory")
		    				Main()
		    	else:
		    		print("\n \033[1;31mError: hampp.conf file not found!")
	    	else:
	    		print("\n \033[1;31mPort length must be 4 digit")
	    		
	    else:
	    		if (path.exists(spath+"HamppServer/core/hampp.conf")):
	    			file = open(spath+"HamppServer/core/hampp.conf", "r")
	    			output = file.read().replace('{{HamppPort}}', '8080')
	    			if(output):
	    				final = output.replace('{{HamppDir}}', '/sdcard/www')
	    				#httpd.conf file replacing
	    				con_file = open(epath+'apache2/httpd.conf', 'wt')
	    				con_file.write(final)
	    				file.close()
	    				con_file.close()
	    				
	    				#Start apache server
	    				os.system('apachectl start')
	    				try:
	    					url = "http://127.0.0.1:8080"
	    					request = requests.get(url)
	    					if "Apache" in request.headers['server']:
	    						print ('''\n\n''')
	    						print ('''\033[1;32m Apache Server Started Succesfully at\033[1;33m''',url,'''\033[1;32mshowing files from \033[1;33m'/sdcard/www'\033[1;32m ..........\033[1;33m\ \033[00m \n\n''')
	    						sleep(0.1)
	    					else:
	    						print("\n \033[1;31mSomething went wrong\n")
	    					Main()
	    				except:
	    					print("\n \033[1;31mApache Starting Failed..... Something error happened...\n")
	    			else:
	    				print("\n \033[1;31mSomething went wrong!")
	    		else:
	    			print("\n \033[1;31mError: hampp.conf file not found!")
	elif choice == '2':
	   	os.system('apachectl stop')
	   	print ('''\n\n''')
	   	print ('''\033[1;32m Apache Server Stopped Succesfully ..........\033[1;33m\ \033[00m \n\n''')
	   	sleep(0.1)
	   	Main()
	elif choice == '3':
	   	print("\n \033[1;32mStarting Mysql Server.........\033[1;33m\ \033[00m \n")
	   	os.system('mysql.server start')
	   	user = getpass.getuser()
	   	print ('''\033[1;32m Mysql Server Started Succesfully at port \033[1;33m3306 \033[1;32mUsername with No Password.\n Login to mysql visiting \033[1;33myourhost:port/phpmyadmin \033[1;32m with-\033[1;33m \n -----------------------------------------------------
|    user:  ''',user,'''                                 |
|    password: (Just put an space in password field)  |
 ----------------------------------------------------- \033[00m\n\n''')
	   	sleep(2)
	   	Main()
	elif choice == '4':
	   	os.system('mysql.server stop')
	   	print ('''\n\n''')
	   	print ('''\033[1;32m Mysql Server Stopped Succesfully ..........\033[1;33m\ \033[00m \n\n''')
	   	sleep(0.1)
	   	Main()
	elif choice == '5':
	   	sys.exit
	else:
	    print('unknown error :| ')
Main()
