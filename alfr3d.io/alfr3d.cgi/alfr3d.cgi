#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# enable debugging
import cgitb

# USAGE:
# ===============
# http://alfr3d.no-ip.org/cgi-bin/alfr3d.cgi?command=Blink
# ===============
import serial
import time
import os
import sys
import cgi
from time import gmtime, strftime, localtime

cgitb.enable()

logfile = '/home/alfr3d/log/alfr3d-cgi.log'

f = open(logfile, 'a')
# for logging purposes
# timestamp = strftime("%H:%M:%S")
f.write("Alfr3d.cgi started: "+strftime("%A, %d %B %Y %H:%M:%S \n", localtime()))

# Create instance of FieldStorage 
form = cgi.FieldStorage() 

# Get data from fields
arg1 = form.getvalue('command')
#arg1 = "Blink"

f.write("received command: "+arg1+"\n")

print "Content-type: text/html\r\n\r\n"
print "<html>"
print "<head>"
print "<title>Alfr3d</title>"
print "</head>"
print "<body>"
print "<h2>Hello!</h2>"
print "Arguments: %s \n" % (arg1)

if (arg1 == "Blink"):
	#arduino = serial.Serial("/dev/ttyUSB0", baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=1)
	arduino = serial.Serial("/dev/ttyACM0", baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=1)
	print("initialising\n")
	f.write("initialising...\n")

	time.sleep(5) # waiting the initialization...
	print("initialized\n")
	f.write("initialisation complete. \n")

	#print "wiring %s \n" % (arg1)
	#arduino.write(arg1)
	arg2 = arg1+"\n"
	f.write("writing to arduino: "+arg2)
	print "writing %s \n" % (arg2)
	arduino.write(arg2)
	f.write("finished writing to arduino: "+strftime("%H:%M:%S \n\n\n"))
elif (arg1 == "welcomehome"):
	print("Welcome Home Sir \n")
	f.write("Welcome Home, Sir \n")
	os.system('/usr/bin/python /home/alfr3d/welcomeHomeSir.py')
	f.write("Finished greeting the master \n")
elif (arg1 == "Check Bonsai"):
	print("Getting humidity readins \n")
	f.write("Getting humidity readins \n")
	os.system('/usr/bin/python /home/alfr3d/bonsai.py')
	f.write("Finished checking the bonsai \n")
elif (arg1 == "Sweep"):
	print("Sweeping servos\n")
	f.write("Sweeping servos\n")
	os.system('/usr/bin/python /home/alfr3d/sweep.py')
	f.write("Finished sweeping the servos\n")

elif (arg1 == "test"):
	print("test\n")
	os.system('/home/alfr3d/tts.sh "It is good to see you up and about" 2>&1')
elif (arg1 == "test2"):
	print("test2\n")
	os.system('touch /home/alfr3d/temp.txt')	

print "<FORM><INPUT Type=\"button\" VALUE=\"Back\" onClick=\"history.go(-1);return true;\"></FORM>"
print "</body>"
print "</html>"

f.close()

