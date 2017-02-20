#!/usr/bin/python

"""
	This is the main Alfr3d daemon running most standard services
"""
# Copyright (c) 2010-2016 LiTtl3.1 Industries (LiTtl3.1).
# All rights reserved.
# This source code and any compilation or derivative thereof is the
# proprietary information of LiTtl3.1 Industries and is
# confidential in nature.
# Use of this source code is subject to the terms of the applicable
# LiTtl3.1 Industries license agreement.
#
# Under no circumstances is this component (or portion thereof) to be in any
# way affected or brought under the terms of any Open Source License without
# the prior express written permission of LiTtl3.1 Industries.
#
# For the purpose of this clause, the term Open Source Software/Component
# includes:
#
# (i) any software/component that requires as a condition of use, modification
#	 and/or distribution of such software/component, that such software/
#	 component:
#	 a. be disclosed or distributed in source code form;
#	 b. be licensed for the purpose of making derivative works; and/or
#	 c. can be redistributed only free of enforceable intellectual property
#		rights (e.g. patents); and/or
# (ii) any software/component that contains, is derived in any manner (in whole
#	  or in part) from, or statically or dynamically links against any
#	  software/component specified under (i).
#

# Imports
import logging
import time
import os										# used to allow execution of system level commands
import sys
import socket
from bottle import route, run, template
from pymongo import MongoClient

# current path from which python is executed
CURRENT_PATH = os.path.dirname(__file__)

# Import my own utilities
sys.path.append(os.path.join(os.path.join(os.getcwd(),os.path.dirname(__file__)),"../"))
import utilities

# set up logging 
logger = logging.getLogger("BottleLog")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.FileHandler(os.path.join(CURRENT_PATH,"../log/alfr3dbottle.log"))
handler.setFormatter(formatter)
logger.addHandler(handler)

# get our own IP
try:
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(("gmail.com",80))
	my_ip = s.getsockname()[0]
	s.close()
	logger.info("Obtained host IP")
except Exception, e:
	log.write(strftime("%H:%M:%S: ")+"Error: Failed to get my IP")
	logger.error("Failed to get host IP")
	logger.error("Traceback "+str(e))

@route('/')
@route('/hello/<name>')
def index(name):
	logger.info("Received request:/hello/"+name)
	return template('<b>Hello {{name}}</b>!', name=name)

@route('/speakString/<command>')
def speakString(command):
	## utilities.speakString(command)	# to be added when speak utility is rebuilt
	logger.info("Received request: speakString")
	return template('<b>Spoke {{string}}</b>!',string=command)

## to be implemented when SPEAK utility is rebuilt!!!
# @route('/speak/<command>')
# def speak(command):
# 	logger.info("Received request: /speak/"+command)
# 	if command == "speakGreeting":
# 		utilities.speakGreeting()
# 	elif command == "speakDate":
# 		utilities.speakDate()
# 	elif command == "speakTime":
# 		utilities.speakTime()
# 	elif command == "speakRandom":
# 		utilities.speakRandom()
# 	elif command == "speakWelcome":
# 		utilities.speakWelcome()
# 	elif command == "speakWeather":
# 		utilities.speakWeather()
# 	elif command == "speakWeather_short":
# 		utilities.speakWeather_short()

# 	return template('<b>Processed request: /speak/{{command}}</b>!',command=command)

@route('/arduino/<command>')
def arduino(command):
	logger.info("Received request: /arduino/"+command)

	if command == "LightsOn":
		utilities.lighting_on()
	elif command == "LightsOff":
		utilities.lighting_off()
	else:
		arduino = utilities.Arduino()
		logger.info("Connecting to Arduino")
		if arduino.connect():
			logger.info("Sending command to Arduino "+command)
			arduino.write(command+"\n")
		else:
			logger.error("Failed to connect to Arduino")

	return template('<b>Roger that {{name}}</b>!', name=command)


@route('/whosthere')
def whosthere():
	logger.info("Received a 'whosthere' requet")

	client = MongoClient('mongodb://ec2-52-89-213-104.us-west-2.compute.amazonaws.com:27017/')
	client.Alfr3d_DB.authenticate("alfr3d","qweQWE123123")
	db = client['Alfr3d_DB']
	usersCollection = db['users']

	count = 0
	users = ""

	# cycle through all users
	for user in usersCollection.find():
		if user['state'] == 'online' and user['location']['name'] == socket.gethostname():
			count +=1
			users += user['name']+'\n'

	return 'online users '+str(count)+' :\n '+users

@route('/<command>')
def processCommand(command):
	logger.info("Received request:/"+command)
	if command == "reboot":
		logger.info("Rebooting")
		os.system('sudo reboot')

	if command == "morningAlarm":
		logger.info('Rise and shine... time for alarm')
		alarm = os.path.join(CURRENT_PATH,"../run/morningAlarm.py")
		os.system("python "+alarm)

	return template('<b>Processed Request {{name}}</b>!', name=command)

run(host=my_ip,port=8080)
