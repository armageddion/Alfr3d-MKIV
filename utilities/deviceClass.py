#!/usr/bin/python

"""
	This is a utility for handling the Devie Class for Alfr3d:
		"==========DEVICE DETAILS============"
		"IP: 		"
		"MAC: 		"
		"state: 		"
		"last online:	"
		"location: 	"						
		"	latitue:	"
		"	longitude:	"
		"user: 		"
		"type: 		"
		"===================================="	
"""
# Copyright (c) 2010-2017 LiTtl3.1 Industries (LiTtl3.1).
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
#     and/or distribution of such software/component, that such software/
#     component:
#     a. be disclosed or distributed in source code form;
#     b. be licensed for the purpose of making derivative works; and/or
#     c. can be redistributed only free of enforceable intellectual property
#        rights (e.g. patents); and/or
# (ii) any software/component that contains, is derived in any manner (in whole
#      or in part) from, or statically or dynamically links against any
#      software/component specified under (i).

import time
import os
import logging
import socket
import ConfigParser
from pymongo import MongoClient

# current path from which python is executed
CURRENT_PATH = os.path.dirname(__file__)

# set up logging 
logger = logging.getLogger("DevicesLog")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
#handler = logging.FileHandler(os.path.join(CURRENT_PATH,"../log/devices.log"))
handler = logging.FileHandler(os.path.join(CURRENT_PATH,"../log/total.log"))
handler.setFormatter(formatter)
logger.addHandler(handler)

# load up all the configs
config = ConfigParser.RawConfigParser()
config.read(os.path.join(os.path.dirname(__file__),'../conf/apikeys.conf'))
# get main DB credentials
db_user = config.get("Alfr3d DB", "user")
db_pass = config.get("Alfr3d DB", "password")

class Device:
	"""
		Device Class for Alfr3d Users' devices
	"""
	name = 'unknown'
	IP = '0.0.0.0'
	MAC = '00:00:00:00:00:00'
	state = 'offline'
	last_online = time.time()
	location = [0,0]
	user = 'unknown'
	deviceType = 'guest'

	# mandatory to pass MAC for robustness
	def newDevice(self, mac):
		exists = self.getDetails(mac)
		if exists:
			logger.error("Device already exists")
			return False

		logger.info("Creating a new device")

		client = MongoClient('mongodb://ec2-52-89-213-104.us-west-2.compute.amazonaws.com:27017/')
		client.Alfr3d_DB.authenticate(db_user,db_pass)
		db = client['Alfr3d_DB']
		devicesCollection = db['devices']

		newDevice = {"name":"unknown",
					 "IP":'0.0,0,0',
					 "MAC":mac,
					 "type":"guest",
					 "state":"online",
					 "location":[0,0],
					 "last_online":int(time.time()),
					 "user":"unknown"}		

		devicesCollection.insert(newDevice)

		return True

	def getDetails(self,mac):
		logger.info("Looking for device with MAC: " + mac)
		client = MongoClient('mongodb://ec2-52-89-213-104.us-west-2.compute.amazonaws.com:27017/')
		client.Alfr3d_DB.authenticate(db_user,db_pass)
		db = client['Alfr3d_DB']
		devicesCollection = db['devices']

		deviceDetails = devicesCollection.find_one({"MAC":mac})

		if not deviceDetails: 
			logger.warn("Failed to find a device with MAC: " + mac + " in the database")
			return False

		logger.info("Device found")
		logger.info(deviceDetails)

		self.name = deviceDetails['name']
		self.type = deviceDetails['type']
		self.IP = deviceDetails['IP']
		self.MAC = deviceDetails['MAC'] 
		self.state = deviceDetails['state']
		self.last_online = deviceDetails['last_online']
		self.location = deviceDetails['location']
		self.user = deviceDetails['user']

		return True

	# Device.setDetails({detail:value, detail2:value2,...})
	def setDetails(self, details):
		client = MongoClient('mongodb://ec2-52-89-213-104.us-west-2.compute.amazonaws.com:27017/')
		client.Alfr3d_DB.authenticate(db_user,db_pass)
		db = client['Alfr3d_DB']
		devicesCollection = db['devices']

		for i in details:
			devicesCollection.update({"MAC":self.MAC},{"$set":{i:details[i]}})

		self.updateHistory()

	# update entire object in DB with latest values
	def update(self):
		client = MongoClient('mongodb://ec2-52-89-213-104.us-west-2.compute.amazonaws.com:27017/')
		client.Alfr3d_DB.authenticate(db_user,db_pass)
		db = client['Alfr3d_DB']
		devicesCollection = db['devices']
		collection_env = db['environment']

		try:
			cur_env = collection_env.find_one({"name":socket.gethostname()})
			devicesCollection.update({"MAC":self.MAC},{"$set":{"name":self.name,
															   "IP":self.IP,
															   "MAC":self.MAC,
															   "type":self.type,
															   "state":self.state,
															   "location":{"name":cur_env['name'],
																		   "city":cur_env['city'],
																		   "state":cur_env['state'],
																		   "country":cur_env['country']},
															   "last_online":int(time.time()),
															   "user":self.user}})
		except Exception, e:
			logger.error("Failed up update device with MAC: "+self.MAC)
			logger.error("Traceback: "+e)
			return False

		logger.info("Device updated")
		self.updateHistory()

		return True

	def updateHistory(self):
		logger.info("Updating device history")
		client = MongoClient('mongodb://ec2-52-89-213-104.us-west-2.compute.amazonaws.com:27017/')
		client.Alfr3d_DB.authenticate(db_user,db_pass)
		db = client['Alfr3d_DB']
		devicesCollection = db['devices']
		historyCollection = db['devices.history']
		collection_env = db['environment']
		
		try:
			deviceDetails = devicesCollection.find_one({"MAC":self.MAC})
			cur_env = collection_env.find_one({"name":socket.gethostname()})
			historyDetails = {	"device":deviceDetails['_id'],
								"location":{"name":cur_env['name'],
											"city":cur_env['city'],
											"state":cur_env['state'],
											"country":cur_env['country']},
								"time":int(time.time())}

			historyCollection.insert(historyDetails)
		except Exception, e:
			logger.error("Failed up update history for device with MAC: "+self.MAC)
			logger.error("Traceback: "+str(e))
			return False
		
		return True

	def display(self):
		result = ""
		result += "==========DEVICE DETAILS============"	+"\n"
		result += "Name: 		"+str(self.name)			+"\n"
		result += "IP: 			"+str(self.IP)				+"\n"
		result += "MAC: 		"+str(self.MAC)				+"\n"
		result += "state: 		"+self.state				+"\n"
		result += "last online:	"+str(self.last_online)		+"\n"
		result += "location: 	"							+"\n"
		result += "				"+str(self.location) 		+"\n"	
		result += "user: 		"+self.user 				+"\n"
		result += "type: 		"+self.deviceType			+"\n"
		result += "===================================="	+"\n"

		print result 
		return result

	def refreshAll(self):
		logger.info("Refreshing device list")

		client = MongoClient('mongodb://ec2-52-89-213-104.us-west-2.compute.amazonaws.com:27017/')
		client.Alfr3d_DB.authenticate(db_user,db_pass)
		db = client['Alfr3d_DB']
		devicesCollection = db['devices']

		# get all devices for that user
		for device in devicesCollection.find():
			# for my devices 5 minute timeout here is more than enough
			# for most devices 15 minutes is fine
			# however, some (brand new) tech is being clever about power saving and if unused will
			# be dormant and, from my observations, only connect once every 20 minutes or so. 
			if time.time() - float(device['last_online']) < 1800: # 30 minutes 
				# set online
				devicesCollection.update({"MAC":device['MAC']},{"$set":{'state':'online'}})	
			else:
				# set offline
				devicesCollection.update({"MAC":device['MAC']},{"$set":{'state':'offline'}})	