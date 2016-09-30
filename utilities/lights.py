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

def lighting_init():
	client = MongoClient('mongodb://ec2-52-89-213-104.us-west-2.compute.amazonaws.com:27017/')
	db = client['Alfr3d_DB']
	devicesCollection = db['devices']

	logger.info("looking for devices")
	for device in devicesCollection.find({"name":'hue'}):
		logger.info("device found: ", device)

		logger.info("looking for apikeys")
		username = config.get("HUE dev", str(device['MAC']).replace(':',''))
		logger.info("found key: ", username)

		bridge = Bridge(device['IP'], username)
		
		logger.info(bridge.lights())
		lights_data = json.loads(json.dumps(bridge.lights()))

		for light in lights_data:
			logger.info("init check; all lights off")
			bridge.lights[light].state(on=False)

		time.sleep(5)

		for light in lights_data:
			logger.info("init check; all lights on")
			bridge.lights[light].state(on=True)	

		time.sleep(5)

		for light in lights_data:
			logger.info("init check; all lights off")
			bridge.lights[light].state(on=False)					

# purely for testing purposes
if __name__ == "__main__":	
	lighting_init()
