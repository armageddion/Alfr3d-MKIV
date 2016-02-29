#!/usr/bin/python

"""
This file is used for all arduino related functions.
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

import serial
import sys
import os
import logging
from time import strftime, sleep

# set up logging 
logger = logging.getLogger("ArduinoLog")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.FileHandler(os.path.join(CURRENT_PATH,"../log/arduino.log"))
handler.setFormatter(formatter)
logger.addHandler(handler)

class Arduino:
	"""
		Arduino family class, embodying common functionality accross the family
	"""

	#def __init__(self, device="/dev/ttyACM0",baudrate=9600):
	def __init__(self, device="/dev/ttyUSB0",baudrate=9600):
		"""
			Class constructor.

			Arguments:
				device		path	:	path to arduino (i.e. /dev/tty/USB0)
				baudrate 	baud 	:	baudrate to use for serial communication
		"""
		
		logger.info("Initializing Arduino\n")
		# bytesize=8, parity='N', stopbits=1, timeout=1

		self.device = device
		self.baudrate = baudrate
		self.bytesize = 8
		self.parity = 'N'
		self.stopbits = 1
		self.timeout = 1

		self.serial = None
		
	def connect(self):
		"""
			Establish serial connection to Arduino
		"""
		logger.info("Connecting to Arduino\n")
		try:
			self.serial = serial.Serial(self.device, self.baudrate, self.bytesize, self.parity, self.stopbits, self.timeout)
			sleep(2)	# need to wait before doing anything else... Arduino needs time... qq
			logger.info("Connected\n")
			return True
		except Exception, e:
			logger.error("Failed to connect to Arduino\n")
			print "Traceback: "+str(e)
			return False

	def readline(self):
		"""
			Read from Arduino
		"""
		logger.info("Reading from Arduino\n")
		try:
			line = self.serial.readline()
			logger.info("Read from Arduino:\n")
			logger.info(line+"\n")
			return True,line
		except:
			logger.error("Failed to read from Arduino\n")
			return False,-1

	def write(self, dataToWrite):
		"""
			Write to Arduino
		"""
		logger.info("Writing "+str(dataToWrite)+" to Arduino\n")
		try:
			self.serial.write(dataToWrite)
			logger.info("Done writing to Arduino\n")
			return True
		except:
			logger.error("Failed to write to Arduino\n")
			return False


