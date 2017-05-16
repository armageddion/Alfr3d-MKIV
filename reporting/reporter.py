#!/usr/bin/python

"""
This file is used for all arduino related functions.
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
#

import os
import json
import requests
import psutil
import socket
import ConfigParser

from pymongo import MongoClient

# load up all the configs
config = ConfigParser.RawConfigParser()
config.read(os.path.join(os.path.dirname(__file__),'../conf/apikeys.conf'))
# get main DB credentials
db_user = config.get("Alfr3d DB", "user")
db_pass = config.get("Alfr3d DB", "password")

def sendReport():
	
	# get system level info
	cpu = psutil.cpu_percent()
	disks = psutil.disk_usage('/')
	memory = psutil.virtual_memory()

	# get latest DB environment info
	# Initialize the database
	client = MongoClient('mongodb://ec2-52-89-213-104.us-west-2.compute.amazonaws.com:27017/')
	client.Alfr3d_DB.authenticate(db_user,db_pass)
	db = client['Alfr3d_DB']

	usersCollection = db['users']
	collection_env = db['environment']
	devicesCollection = db['devices']
	
	# get location info

	try:
		cur_env = collection_env.find_one({"name":socket.gethostname()})
		country = cur_env['country']
		state = cur_env['state']
		city = cur_env['city']
		ip = cur_env['IP']
		try:
			latitude = cur_env['latitude']
			longitude = cur_env['longitude']
		except:
			print "lat/long info is not available"
	except Exception, e:
		print "unable to retreive geo info"	

	data = {
		"status": 1,
		"cpu": cpu,
		"disks":disks.percent,
		"memory":memory.percent
	}

	if cur_env:
		data['environment']={
				"country":country,
				"state":state,
				"city":city,
				"ip":ip
			}
		try:
			data['environment']['lat_long']={
				"latitude":latitude,
				"longitude":longitude
			}
		except:
			print "lat/long info is not available"		

	# get devices info

	try:
		online_devices = devicesCollection.count({"state":"online"})
	except Exception, e:
		print "failed to find number of online devices"

	try: 
		data['online_devices']={"devices":online_devices}
	except Exception, e:
		print "failed to report number of online devices"

	# get users info

	try:
		online_users = usersCollection.count({"state":"online"})
	except Exception, e:
		print "failed to find number of online users"

	try:
		data['online_users']={"online_users":online_users}
		users=[]
		for user in usersCollection.find({"state":"online"}):
			users.append(user['name'])
		data['online_users']['users']={'users':users}
	except Exception, e:
		print "failed to report number of online users"

	# get alfr3d devices info
	peripherals = 0
	data['alfr3d']={"peripherals":peripherals}		
	try:
		light_count = devicesCollection.count({"$and":[
												{"name":'hue'},
												{"state":'online'},
												{"user":'alfr3d'},
												{"location.name":socket.gethostname()}
											]})		
		if light_count != 0:
			peripherals += light_count
			data['alfr3d']['lights']={"status": 1,
									  "count":light_count}
		else:
			data['alfr3d']['lights']={"status": 0,
									  "count":light_count}	
	except Exception, e:
		print "failed to report on lights"

	try:
		coffee_count = devicesCollection.count({"$and":[
												{"name":'coffee'},
												{"state":'online'},
												{"user":'alfr3d'},
												{"location.name":socket.gethostname()}
											]})
		if coffee_count != 0:
			peripherals += coffee_count
			data['alfr3d']['coffee']={"status": 1,
									  "count":coffee_count}
		else:
			data['alfr3d']['coffee']={"status": 0,
									  "count":coffee_count}
	except Exception, e:
		print "failed to report on lights"

	data['alfr3d']={"peripherals":peripherals}		

	# push data out to freeboard
	host = "http://dweet.io/dweet/for/alfr3d.mkv?"
	headers = {"content-type":"application/json","Accept":"text/plain"}

	r = requests.post(host, data=json.dumps(data), headers=headers)

# purely for testing purposes
if __name__ == "__main__":	
	sendReport()