#!/usr/bin/python

"""
	This is environment module for Alfr3d
"""
# Copyright (c) 2010-2014 LiTtl3.1 Industries (LiTtl3.1).
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

import ConfigParser
import os
import sys
import socket
import urllib
import json
import speak
import logging
import weatherUtil
from pymongo import MongoClient
from time import strftime, localtime

# current path from which python is executed
CURRENT_PATH = os.path.dirname(__file__)

# set up logging 
logger = logging.getLogger("EnvironmentLog")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.FileHandler(os.path.join(CURRENT_PATH,"../log/total.log"))
handler.setFormatter(formatter)
logger.addHandler(handler)

config = ConfigParser.RawConfigParser()
config.read(os.path.join(os.path.dirname(__file__),'../conf/apikeys.conf'))

db_user = config.get("Alfr3d DB", "user")
db_pass = config.get("Alfr3d DB", "password")


def checkLocation():

	# get latest DB environment info
	# Initialize the database
	client = MongoClient('mongodb://ec2-52-89-213-104.us-west-2.compute.amazonaws.com:27017/')
	client.Alfr3d_DB.authenticate(db_user,db_pass)
	db = client['Alfr3d_DB']
	collection_env = db['environment']

	try:
		cur_env = collection_env.find_one({"name":socket.gethostname()})
		logger.info("Found environment configuration for this host")
		country = cur_env['country']
		state = cur_env['state']
		city = cur_env['city']
		ip = cur_env['IP']
	except:
		logger.warning("Failed to find environment configuration for this host")
		logger.info("Creating environment configuration for this host")
		country = 'unknown'
		state = 'unknown'
		city = 'unknown'
		ip = 'unknown'


		# Add DB insert of new data!!!!!
		new_environment = {
			'name':socket.gethostname(),
			'country':country,
			'state':state,
			'city':city,
			'IP':ip
		}
		collection_env.insert(new_environment)
		logger.info("new engironment created")

	# placeholders for my ip
	myipv4 = None
	myipv6 = None

	# get my current ip
	logger.info("Getting my IP")
	try:
		myipv4 = urllib.urlopen("http://ipv4bot.whatismyipaddress.com").read()
	except Exception, e:
		logger.error("Error getting my IPV4")
		myipv4 = None
		logger.error("Traceback "+str(e))
		logger.info("Trying to get our IPV6")
		try:
			myipv6 = urllib.urlopen("http://ipv6bot.whatismyipaddress.com").read()
		except Exception, e:
			logger.error("Error getting my IPV6")
			logger.error("Traceback "+str(e))
	finally:
		if not myipv6 and not myipv4:
			return

	# get API key for db-ip.com
	apikey = config.get("API KEY", "dbip")

	# get my geo info
	if myipv6:
		url6 = "http://api.db-ip.com/addrinfo?addr="+myipv6+"&api_key="+apikey
	elif myipv4:
		url4 = "http://api.db-ip.com/addrinfo?addr="+myipv4+"&api_key="+apikey

	country_new = country
	state_new = state
	city_new = city
	ip_new = ip

	logger.info("Getting my location")
	try:
		# try to get our info based on IPV4
		info4 = json.loads(urllib.urlopen(url4).read().decode('utf-8'))

		if info4['city']:
			country_new = info4['country']
			state_new = info4['stateprov']
			city_new = info4['city']
			ip_new = info4['address']

		# if that fails, try the IPV6 way
		else:
			info6 = json.loads(urllib.urlopen(url6).read().decode('utf-8'))
			if info6['country']:
				country_new = info6['country']
				state_new = info6['stateprov']
				city_new = info6['city']
				ip_new = info6['address']		

			else: 
				raise Exception("Unable to get geo info based on IP")

	except Exception, e:
			logger.error("Error getting my location:"+e)
			sys.exit(1)

	if city_new == city:
		logger.info("You are still in the same location")
	else: 
		logger.info("Oh hello! Welcome to "+city_new)
		speak.speakString("Welcome to "+city_new+" sir")
		speak.speakString("I trust you enjoyed your travels")

		# get latest weather info for new location
		weatherUtil.getWeather(city_new, country_new)

	collection_env.update({"name":socket.gethostname()},{"$set":{
				  		   "country":country_new,
						   "state":state_new,
						   "city":city_new,
						   "IP":ip_new}})

# Main - only really used for testing
if __name__ == '__main__':
	checkLocation()	
