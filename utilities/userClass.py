#!/usr/bin/python

"""
	This is a utility for handling the UserClass for Alfr3d:
		"============USER DETAILS============
		"name: 		"
		"state: 		"
		"last online:	"
		"location: 	"				
		"	latitue:	"
		"	longitude:	"
		"type: 		"
		"====================================

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

import os
import logging
import ConfigParser
import socket
from pymongo import MongoClient
from time import time

from deviceClass import Device
from speak import speakWelcome
from lights import nighttime_auto

# we'll want to send notifications to me
from pushbullet import Pushbullet

# current path from which python is executed
CURRENT_PATH = os.path.dirname(__file__)

# set up logging 
logger = logging.getLogger("UsersLog")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
#handler = logging.FileHandler(os.path.join(CURRENT_PATH,"../log/users.log"))
handler = logging.FileHandler(os.path.join(CURRENT_PATH,"../log/total.log"))
handler.setFormatter(formatter)
logger.addHandler(handler)

# get API key for pushbullet
config = ConfigParser.RawConfigParser()
config.read(os.path.join(os.path.dirname(__file__),'../conf/apikeys.conf'))
#apikeys = config.get("API KEY", "pushbullets").split(',')	# for when there are multiples
apikeys = config.get("API KEY", "pushbullet")
# get main DB credentials
db_user = config.get("Alfr3d DB", "user")
db_pass = config.get("Alfr3d DB", "password")


pb = []
try:
	for i in range(len(apikeys)):
		pb.append(Pushbullet(apikeys[i]))
except:
	logger.error("failed to set up pushbullet")
	logger.warn("trying again")
	try:
		pb.append(Pushbullet(apikeys))
	except Exception, e:
		logger.error("failed to set up pushbullet")
		logger.error("Traceback: "+str(e))

class User:
	"""
		User Class for Alfr3d Users
	"""
	name = 'unknown'
	state = 'offline'
	last_online = time()
	location = [0,0]
	userType = 'guest'

	def newUser(self):
		try:
			exists = self.getDetails(self.name)
		except:
			exists = False
		if exists:
			logger.error("User already exists")
			return False

		logger.info("Creating a new user")

		client = MongoClient('mongodb://ec2-52-89-213-104.us-west-2.compute.amazonaws.com:27017/')
		client.Alfr3d_DB.authenticate(db_user,db_pass)
		db = client['Alfr3d_DB']
		usersCollection = db['users']

		newUser = {
			'name': self.name,
			'state' : self.state,
			'last_online' : time(),
			'location' : self.location,
			'type' : self.userType}

		usersCollection.insert(newUser)
		
		return True

	def getDetails(self, name):
		client = MongoClient('mongodb://ec2-52-89-213-104.us-west-2.compute.amazonaws.com:27017/')
		client.Alfr3d_DB.authenticate(db_user,db_pass)
		db = client['Alfr3d_DB']
		usersCollection = db['users']
		userDetails = usersCollection.find_one({"name":name})
		self.name = userDetails['name']
		self.state = userDetails['state']
		self.last_online = userDetails['last_online']
		self.location = userDetails['location']
		self.userType = userDetails['type']

	def setDetails(self, details):
		client = MongoClient('mongodb://ec2-52-89-213-104.us-west-2.compute.amazonaws.com:27017/')
		client.Alfr3d_DB.authenticate(db_user,db_pass)
		db = client['Alfr3d_DB']
		usersCollection = db['users']

		for i in details:
			usersCollection.update({"name":self.name},{"$set":{i:details[i]}})

	def update(self):
		client = MongoClient('mongodb://ec2-52-89-213-104.us-west-2.compute.amazonaws.com:27017/')
		client.Alfr3d_DB.authenticate(db_user,db_pass)
		db = client['Alfr3d_DB']
		usersCollection = db['users']
		collection_env = db['environment']		

		if self.location != usersCollection.find_one({"name":self.name})['location']:
			self.updateHistory()

		try:
			cur_env = collection_env.find_one({"name":socket.gethostname()})
			usersCollection.update({"name":self.name},{"$set":{"name":self.name,
															   "state":self.state,
															   "last_online":str(time()),
															   "location":{"name":cur_env['name'],
																		   "city":cur_env['city'],
																		   "state":cur_env['state'],
																		   "country":cur_env['country']},
															   "type":self.userType}})
		except Exception, e:
			logger.error("Failed up update user: "+self.name)
			logger.error("Traceback: "+e)
			return False

		logger.info("User "+self.name+" updated")

		return True

	def updateHistory(self):
		logger.info("Updating user history")
		client = MongoClient('mongodb://ec2-52-89-213-104.us-west-2.compute.amazonaws.com:27017/')
		client.Alfr3d_DB.authenticate(db_user,db_pass)
		db = client['Alfr3d_DB']
		usersCollection = db['users']
		historyCollection = db['users.history']
		
		try:
			userDetails = usersCollection.find_one({"name":self.name})
			historyDetails = {	"user":userDetails['name'],
								"location":userDetails['location'],
								"time":int(time())}

			historyCollection.insert(historyDetails)
		except Exception, e:
			logger.error("Failed up update history for user: "+self.name)
			logger.error("Traceback: "+e)
			return False
		
		return True

	def display(self):
		result = ""
		result+= "============USER DETAILS============"		+"\n"
		result+= "name: 		"+self.name					+"\n"
		result+= "state: 		"+self.state				+"\n"
		result+= "last online:	"+str(self.last_online)		+"\n"
		result+= "location: 	"							+"\n"
		result+= "				"+str(self.location)		+"\n"	
		result+= "type: 		"+self.userType				+"\n"
		result+= "===================================="		+"\n"

		print result
		return result

	def displayDevices(self):
		client = MongoClient('mongodb://ec2-52-89-213-104.us-west-2.compute.amazonaws.com:27017/')
		client.Alfr3d_DB.authenticate(db_user,db_pass)
		db = client['Alfr3d_DB']
		devicesCollection = db['devices']

		result = ""

		for member in devicesCollection.find({'user':self.name}):
			device = Device()
			device.getDetails(member['MAC'])
			result += device.display()

		return result

	# refreshes state and last_online for all users
	def refreshAll(self):		
		client = MongoClient('mongodb://ec2-52-89-213-104.us-west-2.compute.amazonaws.com:27017/')
		client.Alfr3d_DB.authenticate(db_user,db_pass)
		db = client['Alfr3d_DB']
		devicesCollection = db['devices']
		usersCollection = db['users']
		collection_env = db['environment']

		cur_env = collection_env.find_one({"name":socket.gethostname()})

		# cycle through all users
		for user in usersCollection.find():

			# get current details for each user
			self.getDetails(user['name'])
			last_online=self.last_online

			# get all devices for that user
			for device in devicesCollection.find({"$and":
													[
														{"user":user['name']},
														{'type':{'$ne':'HW'}}
													]}):
				# update last_online time for that user
				if float(device['last_online']) > float(user['last_online']):
					logger.info("Updating user "+user['name'])
					usersCollection.update({"name":user['name']},{"$set":{'last_online':device['last_online']}})
					last_online = device['last_online']

			if time() - float(last_online) < 300:	#10 minutes...
				if self.state == "offline":
					logger.info(user['name']+" just came online")
					# welcome the user
					usersCollection.update({"name":user['name']},{"$set":{'state':'online',	"location":{
																			   "name":cur_env['name'],
																			   "city":cur_env['city'],
																			   "state":cur_env['state'],
																			   "country":cur_env['country']}}})
					nighttime_auto()	# turn on the lights
				 	# speak welcome
				 	speakWelcome(user['name'], time() - float(self.last_online))
				 	for i in range(len(pb)):
				 		try:
						 	pb[i].push_note("Alfr3d", user['name']+" just came online")
						except Exception, e:
							logger.error("Failed to send pushbullet")
							#logger.error("Traceback: "+str(e))
				else:
					usersCollection.update({"name":user['name']},{"$set":{'state':'online',	"location":{
																			   "name":cur_env['name'],
																			   "city":cur_env['city'],
																			   "state":cur_env['state'],
																			   "country":cur_env['country']}}})					
				
			else:
				if self.state == "online":
					logger.info(user['name']+" went offline")
					usersCollection.update({"name":user['name']},{"$set":{'state':'offline'}})	
					nighttime_auto()			# this is only useful when alfr3d is left all alone
					for i in range(len(pb)):
						try:
							pb[i].push_note("Alfr3d", user['name']+" went offline")
						except Exception, e:
							logger.error("Failed to send pushbullet")
							#logger.error("Traceback: "+str(e))	
				else:
					usersCollection.update({"name":user['name']},{"$set":{'state':'offline'}})	

		return True