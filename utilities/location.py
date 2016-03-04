#!/usr/bin/python

"""
	Utility for location related functions
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
#     and/or distribution of such software/component, that such software/
#     component:
#     a. be disclosed or distributed in source code form;
#     b. be licensed for the purpose of making derivative works; and/or
#     c. can be redistributed only free of enforceable intellectual property
#        rights (e.g. patents); and/or
# (ii) any software/component that contains, is derived in any manner (in whole
#      or in part) from, or statically or dynamically links against any
#      software/component specified under (i).

import ConfigParser
import os
import sys
import socket
import urllib
import json
import logging
from time import strftime, localtime

# current path from which python is executed
CURRENT_PATH = os.path.dirname(__file__)

# set up logging 
logger = logging.getLogger("LocLog")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.FileHandler(os.path.join(CURRENT_PATH,"../log/location.log"))
handler.setFormatter(formatter)
logger.addHandler(handler)


def getLocation():
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
		logger.error("Traceback: "+str(e))
		logger.error("Trying to get our IPV6")
		try:
			myipv6 = urllib.urlopen("http://ipv6bot.whatismyipaddress.com").read()
		except Exception, e:
			logger.error("Error getting my IPV6")
			logger.error("Traceback: "+str(e))
	finally:
		if not myipv6 and not myipv4:
			return [False,0,0]

	# get API key for db-ip.com
	config = ConfigParser.RawConfigParser()
	config.read(os.path.join(os.path.dirname(__file__),'../config/apikeys.conf'))
	apikey = config.get("API KEY", "dbip")

	# get my geo info
	if myipv6:
		url6 = "http://api.db-ip.com/addrinfo?addr="+myipv6+"&api_key="+apikey
	elif myipv4:
		url4 = "http://api.db-ip.com/addrinfo?addr="+myipv4+"&api_key="+apikey

	country_new = ''
	state_new = ''
	city_new = ''
	ip_new = ''


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
		logger.error("Error getting my location")
		logger.error("Traceback: "+str(e))
		return [False,0,0]


	logger.info("IP:"+str(ip_new))
	logger.info("City:"+str(city_new))
	logger.info("Sate/Prov:"+str(state_new))
	logger.info("Country:"+str(country_new))	

	return [True, city_new, country_new]
