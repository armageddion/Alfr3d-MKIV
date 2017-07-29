#!/usr/bin/python

"""
	This is the utility for watering flowers
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
import requests	
import ConfigParser
from bottle import route, run, template
from pymongo import MongoClient

# current path from which python is executed
CURRENT_PATH = os.path.dirname(__file__)

# Import my own utilities
sys.path.append(os.path.join(os.path.join(os.getcwd(),os.path.dirname(__file__)),"../"))
import utilities

# set up logging 
logger = logging.getLogger("IrrigationLog")
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


logger.info("Received request to water the flowers")
secret = config.get("API KEY", "ifttt_hook")

def water_flowers(timeout=10):
	flower_on_request = requests.post("https://maker.ifttt.com/trigger/water_flowers/with/key/"+str(secret))
	if flower_on_request.status_code == 200:
		logger.info("successfully turned on the irrigation system")

		time.sleep(timeout)
		
		flower_off_request = requests.post("https://maker.ifttt.com/trigger/water_flowers_end/with/key/"+str(secret))
		if flower_off_request.status_code == 200:
			logger.info("successfully turned off the irrigation system")
		else:
			logger.error("something went wrong. unable to turn off the irrigation system")
	else:
		logger.error("something went wrong. unable to turn off the irrigation system")

if __name__ == "__main__":
	if len(sys.argv) == 2:
		try:
			water_flowers(sys.argv[1])
		except Exception, e:
			logger.error("Failed to water flowers")
			logger.error("Traceback: "+str(e))
	else:
		water_flowers()	