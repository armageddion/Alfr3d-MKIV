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
import logging
import socket
import ConfigParser
import soundcloud					# soundcloud api
import pychromecast					# cast music to chromecast
from qhue import Bridge
from pymongo import MongoClient

# current path from which python is executed
CURRENT_PATH = os.path.dirname(__file__)

# set up logging 
logger = logging.getLogger("AudioLog")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.FileHandler(os.path.join(CURRENT_PATH,"../log/total.log"))
handler.setFormatter(formatter)
logger.addHandler(handler)

# load up all the configs
config = ConfigParser.RawConfigParser()
config.read(os.path.join(os.path.dirname(__file__),'../conf/apikeys.conf'))
# get soundcloud credentials
sc_cli_id = config.get("SoundCloud", "client_id")
sc_secret = config.get("SoundCloud", "client_secret")

def authorize():
	# create client object with app credentials
	client = soundcloud.Client(client_id=sc_cli_id,
							   client_secret=sc_secret,
							   redirect_uri='http://alfr3d.io')

	# redirect user to authorize URL
	redirect = client.authorize_url()	
	# code obtained = 8a4defe51adf38e0ca8a55fa1ad6679e

	# exchange authorization code for access token
	code = params['code']
	access_token = client.exchange_token(code)
	access_token.access_token 	# actual token u'1-276621-78238311-683aee13cdccf0'
	#access_token.refresh_token
	#access_token.expires_in
	#access_token.scope

def sc_check():
	access_token = config.get("SoundCloud", "token")
	client = soundcloud.Client(access_token=access_token)

	current_user = client.get('/me').username
	print current_user

def play():
	os.system('omxplayer -o local '+os.path.join(CURRENT_PATH,'../tmp/audio.mp3'))


def playMorningMedia():
	# time to make chromecast do some work
	chromecasts = pychromecast.get_chromecasts()
	cast = next(cc for cc in chromecasts if cc.device.friendly_name == "ArmageddionCast")
	cast.wait()
	media_controller = cast.media_controller
	# stream comes from here http://www.181.fm/?p=mp3links
	media_controller.play_media("http://listen.181fm.com/181-breeze_128k.mp3", 'audio/mp3')	

# purely for testing purposes
if __name__ == "__main__":	
	sc_check()
