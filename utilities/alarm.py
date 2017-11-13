#!/usr/bin/python

"""
	This is my morning alarm and briefing
	and various greetings throughout the day
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
import sys
import logging
import time
import ConfigParser								# used to parse alfr3ddaemon.conf
import datetime
from random import randint
from pymongo import MongoClient					# database link 

import speak
import location
import weatherUtil
import audio
import userClass
import googleUtil

# current path from which python is executed
CURRENT_PATH = os.path.dirname(__file__)

# set up logging 
logger = logging.getLogger("AlarmLog")
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

def smartAlarm():
	"""
		Description:
			morning alarm function.

		### TO DO - rework this whole utility as a generic smart alarm
		### purpose specific alarms are written separately
	"""
	logger.info("Time to ring alarm")
	speak.speakGreeting()
	if (datetime.datetime.now().hour > 5) and (datetime.datetime.now().hour <= 12):
		logger.info("Good Morning!")
		speak.speakString("your time to rest has come to an end")
		speak.speakTime()
		speak.speakDate()

		loc = location.getLocation()
		weatherUtil.getWeather(loc[1],loc[2])

		unread_count = speak.getUnreadCount()	# not sure why i did this 
		if unread_count > 1:
			speak.speakString("While you were sleeping "+str(unread_count)+" emails flooded your inbox")
		
		try:	
			audio.playMorningMedia()
		except Exception, e:
			logger.error("Failed to play alarm music")
			logger.error("Traceback: "+str(e))

		return

	elif (datetime.datetime.now().hour >= 21):
		logger.info("Evening alarm perhaps? night even?")
		speak.speakTime()

		owner = userClass.User()
		owner.getDetails("armageddion")
		ishome = owner.state
		if (ishome == 'online'):
			logger.info("Bed time, maybe?")

			quips = [
				"Unless we are burning the midnight oil, ",
				"If you are going to invent something new tomorrow, ",
				"If you intend on being charming tomorrow, "]

			tempint = randint(1,len(quips))

			greeting = quips[tempint-1]
			greeting += "perhaps you should consider getting some rest."

			speak.speakString(greeting)		

			event_tomorrow = googleUtil.calendarTomorrow()
			event_tomorrow_title = event_tomorrow['summary']
			event_tomottow_time = datetime.datetime.strptime( event_tomorrow['start'].get('dateTime').split("T")[1][:-6][:5], '%H:%M')

			speak.speakString("Your first event tomorrow is "+event_tomorrow_title+" at "+str(event_tomottow_time.hour))

			return

def sunriseAlarm():
	"""
		Description:
			Pre-sunrise alarm giving users a chance to get up in time to see sunrise
	"""	
	logger.info("Time for pre-sunrise alarm")
	speak.speakGreeting()
	speak.speakString("in case you are awake,")
	
	quips = [
		"consider going out to watch sunrise",
		"sun will rise soon. I thought you might be interested to know"]

	tempint = randint(1,len(quips))
	greeting = quips[tempint-1]
	speak.speakGreeting(greeting)

# purely for testing purposes
if __name__ == "__main__":	
	smartAlarm()