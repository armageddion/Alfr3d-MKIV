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

import os
import sys
import socket
import logging
import ConfigParser
import json
import bottle
from bottle import route, run, template, request, redirect, response
from time import gmtime, strftime, localtime, sleep, time		# needed to obtain time
from pymongo import MongoClient

# current path from which python is executed
CURRENT_PATH = os.path.dirname(__file__)

# Import my own utilities - not needed for API server
#sys.path.append(os.path.join(os.path.join(os.getcwd(),os.path.dirname(__file__)),"../"))
#import utilities

# set up logging 
logger = logging.getLogger("ServerBottleLog")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.FileHandler(os.path.join(CURRENT_PATH,"../log/total.log"))
handler.setFormatter(formatter)
logger.addHandler(handler)

# get API key for pushbullet
config = ConfigParser.RawConfigParser()
config.read(os.path.join(os.path.dirname(__file__),'../conf/apikeys.conf'))
# get main DB credentials
db_user = config.get("Alfr3d DB", "user")
db_pass = config.get("Alfr3d DB", "password")


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

class EnableCors(object):
	name = 'enable_cors'
	api = 2

	def apply(self, fn, context):
		def _enable_cors(*args, **kwargs):
			# set CORS headers
			response.headers['Access-Control-Allow-Origin'] = '*'
			response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
			response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

			if bottle.request.method != 'OPTIONS':
				# actual request; reply with the actual response
				return fn(*args, **kwargs)

		return _enable_cors

app = bottle.app()

@app.route('/')
def index(name="guest"):
	logger.info("Received request:/hello/"+name)
	return template('<b>Hello {{name}}</b>!', name=name)

# http://www.littl31.com:8080/whosthere?host=<hostname>
@app.route('/whosthere')
def whosthere():
	if len(request.query)==0:
		logger.info("Received a 'whosthere' requet")
		client = MongoClient('mongodb://localhost:27017/')
		client.Alfr3d_DB.authenticate(db_user,db_pass)
		db = client['Alfr3d_DB']
		usersCollection = db['users']

		count = 0
		users = []

		# cycle through all users
		#for user in usersCollection.find():
		for user in usersCollection.find({"state":'online'}):
				count +=1
				users.append(user['name'])

		response.headers['Content-type'] = 'application/json'
		result = {}
		result['location'] = "all locations"
		if count > 0:
			result['users']=[]
			for i in range(len(users)):
				result['users'].append(users[i])
		else:
			result['users']=0

		return json.dumps(result)		

	elif request.query.host:
		logger.info("Received a 'whosthere' requet for host "+str(request.query.host))
		client = MongoClient('mongodb://localhost:27017/')
		client.Alfr3d_DB.authenticate(db_user,db_pass)
		db = client['Alfr3d_DB']
		usersCollection = db['users']

		count = 0
		users = []

		# cycle through all users
		#for user in usersCollection.find():
		for user in usersCollection.find({"$and":[
												{"state":'online'},
												{"location.name":request.query.host}
											]}):
				count +=1
				users.append(user['name'])


		response.headers['Content-type'] = 'application/json'
		result = {}
		result['location'] = request.query.host
		if count > 0:
			result['users']=[]
			for i in range(len(users)):
				result['users'].append(users[i])
		else:
			result['users']=0

		return json.dumps(result)		
	else:
		logger.info("Received a 'whosthere' requet: "+str(request.query_string))
		logger.warn("and I dont know what to do with that...")
		return template('<b>There is a problem between the keyboard and the chair. Fix your query {{name}}</b>!', name=request.query_string)

# /user/get?name=<name>
@app.route('/user/<command>')
def user(command):
	print "WIP"

	result = {}

	if request.query.get('name'):
		name = request.query.get('name')
		print "name: "+name
	else:
		print "please provide user name"
		result['error']="please provide user name"
		return json.dumps(result)

	# getUser
	if command == 'get':
		logger.info("getting user details for user "+name)

		try:
			client = MongoClient('mongodb://localhost:27017/')
			client.Alfr3d_DB.authenticate(db_user,db_pass)
			db = client['Alfr3d_DB']
			usersCollection = db['users']
			userDetails = usersCollection.find_one({"name":name})
		except Exception, e:
			logger.error("failed to find user "+name)
			logger.error("traceback: "+str(e))

		try:
			result['username'] = request.query.name
			result['username']['state'] = userDetails['state']
			result['username']['last_online'] = userDetails['last_online']
			result['username']['location'] = userDetails['location']
			result['username']['userType'] = userDetails['type']		
			return json.dumps(result)
		except Exception, e:
			logger.error("failed to find user "+name)
			logger.error("traceback: "+str(e))			

	# TODO
	elif command == 'set':
		print "updating user "+ name
		resut['error']="user update feature is not yet implemented"
		return json.dumps(result)		

	logger.info("Received a 'user' requet: "+str(request.query_string))
	logger.warn("and I dont know what to do with that...")
	return template('<b>There is a problem between the keyboard and the chair. Fix your query {{name}}</b>!', name=request.query_string)

# /device/get?MAC=<mac>
@app.route('/device/<command>')
def device(command):
	print "WIP"
	print request

	result = ""

	if request.query.get('MAC'):
		mac = request.query.get('MAC')
		print "MAC: "+mac
	else:
		print "please provide device mac"
		return template('<b>please provide device mac</b>!')

	# getDevice
	if command == 'get':
		print "getting device details for device with MAC "+mac
		
		device = utilities.Device()
		try:
			device.getDetails(mac)
		except Exception, e:
			print "failed to find device wiht MAC "+mac
			print "traceback: "+str(e)	
			return template('<b>failed to find device wiht MAC '+mac+'</b>!')
		
		result += device.display()

		return template(txt2HTML(result))

	# TODO
	elif command == 'set':
		print "updating device with MAC "+ mac
		updateList = {}
		device = utilities.Device()
		try:
			device.getDetails(mac)
		except Exception, e:
			print "failed to find device wiht MAC "+mac
			print "traceback: "+str(e)
			return template('<b>failed to find device wiht MAC '+mac+'</b>!')

		if request.query.get('IP'):
			updateList['IP'] = request.query.get('IP')
		if request.query.get('state'):
			updateList['state'] = request.query.get('state')
		if request.query.get('last_online'):
			updateList['last_online'] = request.query.get('last_online')
		else:
			updateList['last_online'] = time()
		if request.query.get('location'):
			loc = []
			for i in request.query.get('location').split(","):
				loc.append(float(i))
			updateList['location'] = loc
		if request.query.get('user'):
			updateList['user'] = request.query.get('user')			
		if request.query.get('deviceType'):
			updateList['deviceType'] = request.query.get('deviceType')			

		# set device details
		try:
			device.setDetails(updateList)
		except Exception, e:
			print "failed to update device wiht MAC "+mac
			print "traceback: "+str(e)	
			return template('<b>failed to update device wiht MAC '+mac+'</b>!')

		# update last_online time for the corresponding user
		try:
			user = utilities.User()
			user.getDetails(device.user)
			user.setDetails({'last_online':updateList['last_online']})
		except Exception, e:
			print "failed to update last seen time for user "+device.user
			print "traceback: "+str(e)	
			return template('<b>failed to update last seen time for user '+device.user+'</b>!')

		redirect('/device/get?MAC='+mac)		
			
@app.route ('/instance/<command>')
def instance(command):
	print "TODO"

def txt2HTML(txt):
	result = "<HTML><HEAD><TITLE>Alfr3d:Results</TITLE></HEAD><BODY>\n"
	arr = txt.split('\n')
	for i in range(len(arr)):
		result += "<p>"
		result += arr[i]
		result += "</p>"

	result += "</HTML></BODY>\n"
	return result

app.install(EnableCors())	
app.run(host=my_ip,port=8080)