#!/usr/bin/python

"""
	This is my morning alarm and briefing
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

import os
import sys
import logging
from random import randint
from time import time, strftime, localtime

import speak
import location
import weatherUtil

# current path from which python is executed
CURRENT_PATH = os.path.dirname(__file__)

# set up logging 
logger = logging.getLogger("AlarmLog")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.FileHandler(os.path.join(CURRENT_PATH,"../log/total.log"))
handler.setFormatter(formatter)
logger.addHandler(handler)

def morningAlarm():
	"""
		Description:
			morning alarm function.
	"""
	logger.info("Time to ring morning alarm")
	try:
		speak.speakGreeting()
		if (strftime("%p",localtime()) == "AM"):
			speak.speakString("your time to rest has come to an end")
			speak.speakTime()
			speak.speakDate()

			loc = location.getLocation()
			weatherUtil.getWeather(loc[1],loc[2])

			unread_count = speak.getUnreadCount()
			if unread_count > 1:
				speak.speakString("While you were sleeping "+str(unread_count)+" emails flooded your inbox")
			return

		else:
			speak.speakTime()

			random = [
				"Unless we are burning the midnight oil, ",
				"If you are going to invent something new tomorrow, ",
				"If you intend on being charming tomorrow, "]

			tempint = random.randint(1,len(random))

			greeting = random[tempint-1]
			greeting += "perhaps you should consider getting some rest."

			speak.speakString(greeting)		
			return

	except Exception, e:
		logger.error("Failed to ring the morning alarm")
		logger.error("Traceback "+str(e))

# purely for testing purposes
if __name__ == "__main__":	
	morningAlarm()