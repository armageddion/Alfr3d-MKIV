#!/usr/bin/python

"""
This file is used for all lighting functions.
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
#

import os
import json
import time
import logging
import ConfigParser
from qhue import Bridge
from pymongo import MongoClient

# current path from which python is executed
CURRENT_PATH = os.path.dirname(__file__)

# set up logging 
logger = logging.getLogger("LightsLog")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.FileHandler(os.path.join(CURRENT_PATH,"../log/total.log"))
handler.setFormatter(formatter)
logger.addHandler(handler)

# get username key for the hue
config = ConfigParser.RawConfigParser()
config.read(os.path.join(os.path.dirname(__file__),'../conf/apikeys.conf'))

class light_hue():
	"""
		a class for each hue light we've got
	"""
	number = 1
	ip = ''
	username = ''

	def hue_on(self):
		bridge = Bridge(self.ip, self.username)
		bridge.lights[self.number].state(on=True)

	def hue_off(self):
		bridge = Bridge(self.ip, self.username)
		bridge.lights[self.number].state(on=False)

	def hue_toggle(self):
		bridge = Bridge(self.ip, self.username)
		print bridge.lights[self.number]()['state']['on']
		if bridge.lights[self.number]()['state']['on']:
			self.hue_off()
		else:
			self.hue_on()

def lighting_init():
	client = MongoClient('mongodb://ec2-52-89-213-104.us-west-2.compute.amazonaws.com:27017/')
	client.Alfr3d_DB.authenticate("alfr3d","qweQWE123123")
	db = client['Alfr3d_DB']
	devicesCollection = db['devices']

	logger.info("looking for devices")
	for device in devicesCollection.find({"name":'hue'}):
		logger.info("device found: "+ str(device))

		logger.info("looking for apikeys")
		username = config.get("HUE dev", str(device['MAC']).replace(':',''))
		logger.info("found key: "+ str(username))

		bridge = Bridge(device['IP'], username)
		
		logger.info(str(bridge.lights()))
		lights_data = json.loads(json.dumps(bridge.lights()))

		for light in lights_data:
			hue = light_hue()
			hue.number=light
			hue.ip = device['IP']
			hue.username = username

			logger.info("init check; all lights off")
			hue.hue_off()

		time.sleep(2)

		for light in lights_data:
			logger.info("init check; all lights on")
			#bridge.lights[light].state(on=True)	
			hue.hue_on()

		time.sleep(2)

		for light in lights_data:
			logger.info("init check; all lights off")
			#bridge.lights[light].state(on=False)					
			hue.hue_off()

# turns all hue lights off
def lighting_off():
	client = MongoClient('mongodb://ec2-52-89-213-104.us-west-2.compute.amazonaws.com:27017/')
	client.Alfr3d_DB.authenticate("alfr3d","qweQWE123123")
	db = client['Alfr3d_DB']
	devicesCollection = db['devices']

	logger.info("looking for devices")
	for device in devicesCollection.find({"name":'hue'}):
		logger.info("device found: "+ str(device))

		logger.info("looking for apikeys")
		username = config.get("HUE dev", str(device['MAC']).replace(':',''))
		logger.info("found key: "+ str(username))

		bridge = Bridge(device['IP'], username)
		
		logger.info(str(bridge.lights()))
		lights_data = json.loads(json.dumps(bridge.lights()))

		for light in lights_data:
			hue = light_hue()
			hue.number=light
			hue.ip = device['IP']
			hue.username = username

			logger.info("all lights off")
			hue.hue_off()

# turns all hue lights off
def lighting_on():
	client = MongoClient('mongodb://ec2-52-89-213-104.us-west-2.compute.amazonaws.com:27017/')
	client.Alfr3d_DB.authenticate("alfr3d","qweQWE123123")
	db = client['Alfr3d_DB']
	devicesCollection = db['devices']

	logger.info("looking for devices")
	for device in devicesCollection.find({"name":'hue'}):
		logger.info("device found: "+ str(device))

		logger.info("looking for apikeys")
		username = config.get("HUE dev", str(device['MAC']).replace(':',''))
		logger.info("found key: "+ str(username))

		bridge = Bridge(device['IP'], username)
		
		logger.info(str(bridge.lights()))
		lights_data = json.loads(json.dumps(bridge.lights()))

		for light in lights_data:
			hue = light_hue()
			hue.number=light
			hue.ip = device['IP']
			hue.username = username

			logger.info("all lights on")
			hue.hue_on()

# purely for testing purposes
if __name__ == "__main__":	
	lighting_init()
