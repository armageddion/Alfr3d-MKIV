#!/usr/bin/python

"""
	This is a utility for music playback
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
import ConfigParser								# used to parse alfr3ddaemon.conf
import spotipy 									# third party spotify library~
import logging
import spotipy.util as sp_util

# import my own utilities
sys.path.append(os.path.join(os.path.join(os.getcwd(),os.path.dirname(__file__)),"../"))

# current path from which python is executed
CURRENT_PATH = os.path.dirname(__file__)

# set up logging 
logger = logging.getLogger("MusicLog")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
#handler = logging.FileHandler(os.path.join(CURRENT_PATH,"../log/speak.log"))
handler = logging.FileHandler(os.path.join(CURRENT_PATH,"../log/total.log"))
handler.setFormatter(formatter)
logger.addHandler(handler)

# get API key for db-ip.com
config = ConfigParser.RawConfigParser()
config.read(os.path.join(CURRENT_PATH,'../conf/apikeys.conf'))
client_username 	= config.get("Spotify", "username")
client_id 			= config.get("Spotify","id")
client_secret 		= config.get("Spotify","secret")
client_redirect_uri = config.get("Spotify","redirect_uri")

def init_spotipy():
	# Necessary environment variables for this to work... 

	os.environ['SPOTIPY_CLIENT_ID']=client_id
	os.environ['SPOTIPY_CLIENT_SECRET']=client_secret
	os.environ['SPOTIPY_REDIRECT_URI']=client_redirect_uri

	#token = sp_util.prompt_for_user_token(client_username, 'playlist-read-private')		# other scopes available at: https://developer.spotify.com/web-api/using-scopes/
	token = sp_util.prompt_for_user_token(client_username, 'user-library-read')

def init_soundcloud():
	logger.info("initializing soundcloud services")

# Main - only really used for testing
if __name__ == '__main__':
	#init_spotipy()							# SPOTIFY DOESN"T ALLOW PLAYBACK!!!!
	init_soundcloud()