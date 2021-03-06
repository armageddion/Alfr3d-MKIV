#!/usr/bin/python

"""
This file is used for all lighting functions.
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
import time
import datetime
import logging
import socket
import requests			
import ConfigParser
from qhue import Bridge
from pymongo import MongoClient

import alarm

# current path from which python is executed
CURRENT_PATH = os.path.dirname(__file__)

# set up logging 
logger = logging.getLogger("LightsLog")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.FileHandler(os.path.join(CURRENT_PATH,"../log/total.log"))
handler.setFormatter(formatter)
logger.addHandler(handler)

# load up all the configs
config = ConfigParser.RawConfigParser()
config.read(os.path.join(os.path.dirname(__file__),'../conf/apikeys.conf'))
# get main DB credentials
db_user = config.get("Alfr3d DB", "user")
db_pass = config.get("Alfr3d DB", "password")

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

def lightingInit():
	client = MongoClient('mongodb://ec2-52-89-213-104.us-west-2.compute.amazonaws.com:27017/')
	client.Alfr3d_DB.authenticate(db_user,db_pass)
	db = client['Alfr3d_DB']
	devicesCollection = db['devices']

	logger.info("looking for devices")
	#for device in devicesCollection.find({"name":'hue'}):
	light_count = devicesCollection.count({"$and":[
											{"type":'lights'},
											{"state":'online'},
											{"user":'alfr3d'},
											{"location.name":socket.gethostname()}
										]})
	if light_count != 0:
		logger.info("found "+str(light_count)+" lights")
	else:
		logger.warn("unable to find any lights.. :(")
		raise Exception("no lights online")

	for device in devicesCollection.find({"$and":[
											{"type":'lights'},
											{"location.name":socket.gethostname()}
										]}):
		logger.info("device found: "+ str(device))
		
		if device['name'].startswith("hue"):
			logger.info("initialising all Hue lights")
			
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

		if device['name'].startswith("Lifx"):
			logger.info("initialising all Lifx lights")
			lifx_token = config.get("Lifx", "token")

			headers = {"Authorization": "Bearer %s" % lifx_token,}
			response = requests.get('https://api.lifx.com/v1/lights/all', headers=headers)
			if response.status_code != 200:
				logger.error("failed to authenticate with Lifx subsystems")
			else:
				logger.info("successfully authenticated with Lifx subsystems")
				for bulb in response.json():
					bulb_label = bulb[u'label']
					if bulb[u'connected'] != True:
						logger.warn("bulb "+str(bulb_label)+" is not online")
					else:
						if bulb[u'power'] != u'off':
							response = requests.put('https://api.lifx.com/v1/lights/label:'+bulb_label+'/state', data={"power": "off"}, headers=headers)
							if response.json()[u'results'][0][u'status'] != u'ok':
								logger.error("failed to turn off the bulb "+str(bulb_label))
							time.sleep(2)
						response = requests.put('https://api.lifx.com/v1/lights/label:'+bulb_label+'/state', data={"power": "on"}, headers=headers)
						if response.json()[u'results'][0][u'status'] != u'ok':
							logger.error("failed to turn on the bulb "+str(bulb_label))						
						time.sleep(2)
						response = requests.put('https://api.lifx.com/v1/lights/label:'+bulb_label+'/state', data={"power": "off"}, headers=headers)
						if response.json()[u'results'][0][u'status'] != u'ok':
							logger.error("failed to turn off the bulb "+str(bulb_label))						
			### TODO

# turns all hue lights off
def lightingOff():
	client = MongoClient('mongodb://ec2-52-89-213-104.us-west-2.compute.amazonaws.com:27017/')
	client.Alfr3d_DB.authenticate(db_user,db_pass)
	db = client['Alfr3d_DB']
	devicesCollection = db['devices']

	logger.info("looking for devices")
	for device in devicesCollection.find({"$and":[
											{"type":'lights'},
											{"location.name":socket.gethostname()}
										]}):
		logger.info("device found: "+ str(device))

		if device['name'].startswith("hue"):
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

		elif device['name'].startswith("Lifx"):
			bulb_label = device['name']
			logger.info("looking for apikeys")
			lifx_token = config.get("Lifx", "token")
			logger.info("found key: "+ str(lifx_token))

			headers = {"Authorization": "Bearer %s" % lifx_token,}
			response = requests.put('https://api.lifx.com/v1/lights/label:'+bulb_label+'/state', data={"power": "off"}, headers=headers)
			if response.json()[u'results'][0][u'status'] != u'ok':
				logger.error("failed to turn off the bulb "+str(bulb_label))			

# turns all hue lights off
def lightingOn():
	client = MongoClient('mongodb://ec2-52-89-213-104.us-west-2.compute.amazonaws.com:27017/')
	client.Alfr3d_DB.authenticate(db_user,db_pass)
	db = client['Alfr3d_DB']
	devicesCollection = db['devices']

	logger.info("looking for devices")
	for device in devicesCollection.find({"$and":[
											{"type":'lights'},
											{"location.name":socket.gethostname()}
										]}):
		logger.info("device found: "+ str(device))

		if device['name'].startswith("hue"):
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

		elif device['name'].startswith("Lifx"):
			bulb_label = device['name']
			logger.info("looking for apikeys")
			lifx_token = config.get("Lifx", "token")
			logger.info("found key: "+ str(lifx_token))

			headers = {"Authorization": "Bearer %s" % lifx_token,}
			response = requests.put('https://api.lifx.com/v1/lights/label:'+bulb_label+'/state', data={"power": "on"}, headers=headers)
			if response.json()[u'results'][0][u'status'] != u'ok':
				logger.error("failed to turn off the bulb "+str(bulb_label))


def nighttime_auto():
	logger.info("entering nightlight mode")

	client = MongoClient('mongodb://ec2-52-89-213-104.us-west-2.compute.amazonaws.com:27017/')
	client.Alfr3d_DB.authenticate(db_user,db_pass)
	db = client['Alfr3d_DB']	

	usersCollection = db['users']
	envCollection = db['environment']

	usercount = usersCollection.count({"$and":[
											{"state":"online"},
											{"location.name":socket.gethostname()}
										]})
	if usercount < 2:  # note: alfr3d is a user
		logger.info("no need to turn on the lights just for alfr3d")
		lightingOff()
		return

	env = envCollection.find_one({"name":socket.gethostname()})
	try:
		sunset = int(env['weather']['sunset'])
		sunset_time = datetime.datetime.now().replace(hour=int(time.strftime('%H',time.localtime(sunset))), 
													  minute=int(time.strftime("%M",time.localtime(sunset)))
													  	)
	except Exception, e:
		logger.error("Failed to find out the time of sunset")
		logger.error("Traceback: "+str(e))						
		return

	if datetime.datetime.now() < sunset_time:
		logger.info("sun hasnt set yet")
		return

	lifx_token = config.get("Lifx", "token")

	headers = {"Authorization": "Bearer %s" % lifx_token,}
	response = requests.get('https://api.lifx.com/v1/lights/all', headers=headers)
	if response.status_code != 200:
		logger.error("failed to authenticate with Lifx subsystems")
	else:
		logger.info("successfully authenticated with Lifx subsystems")
		for bulb in response.json():
			bulb_label = bulb[u'label']
			if bulb[u'connected'] != True:
				logger.warn("bulb "+str(bulb_label)+" is not online")
			else:
				response = requests.put('https://api.lifx.com/v1/lights/label:'+bulb_label+'/state', data={"power": "on"}, headers=headers)
				if response.json()[u'results'][0][u'status'] != u'ok':
					logger.error("failed to turn on the bulb "+str(bulb_label))	

# purely for testing purposes
if __name__ == "__main__":	
	lightingInit()
