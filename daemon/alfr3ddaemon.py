#!/usr/bin/python

"""
	This is the main Alfr3d daemon running most standard services
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
import re
import sys
import socket
import schedule									# 3rd party lib used for alarm clock managment. 
import ConfigParser								# used to parse alfr3ddaemon.conf
from pymongo import MongoClient					# database link 
from threading import Thread
from daemon import Daemon
from random import randint						# used for random number generator

# current path from which python is executed
CURRENT_PATH = os.path.dirname(__file__)

# import my own utilities
sys.path.append(os.path.join(os.path.join(os.getcwd(),os.path.dirname(__file__)),"../"))
import utilities
import reporting

# set up daemon things
os.system('sudo mkdir -p /var/run/alfr3ddaemon')
#os.system('sudo chown alfr3d:alfr3d /var/run/alfr3ddaemon')

# load up all the configs
config = ConfigParser.RawConfigParser()
config.read(os.path.join(os.path.dirname(__file__),'../conf/apikeys.conf'))
# get main DB credentials
db_user = config.get("Alfr3d DB", "user")
db_pass = config.get("Alfr3d DB", "password")

# gmail unread count
unread_Count = 0
unread_Count_new = 0

# various counters to be used for pacing spreadout functions
quipStartTime = time.time()
waittime_quip = randint(5,10)

# set up logging 
logger = logging.getLogger("DaemonLog")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
#handler = logging.FileHandler(os.path.join(CURRENT_PATH,"../log/alfr3ddaemon.log"))
handler = logging.FileHandler(os.path.join(CURRENT_PATH,"../log/total.log"))
handler.setFormatter(formatter)
logger.addHandler(handler)

# schedule morning alarm
schedule.every().day.at("8:30").do(utilities.morningAlarm)

class MyDaemon(Daemon):		
	def run(self):
		while True:
			"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
				Logging Examples:
				logger.debug("Debug message")
				logger.info("Info message")
				logger.warn("Warning message")
				logger.error("Error message")
			"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

			"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
			block to update location if changed
			"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
			# try:
			# 	logger.info("Running a geoscan")
			# 	utilities.getLocation()
			# except Exception, e:
			# 	logger.error("Failed to complete geoscan scan")
			# 	logger.error("Traceback "+str(e))

			"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
				Check online members
			"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
			try:
				logger.info("Scanning network")
				utilities.checkLANMembers()
			except Exception, e:
				logger.error("Failed to complete network scan")
				logger.error("Traceback: "+str(e))			

			"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
				Send a report out
			"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""				
			try:
				logger.info("Creating a system report")
				reporting.sendReport()
			except Exception, e:
				logger.error("Failed to send report")
				logger.error("Traceback: "+str(e))	

			"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
				block to operate lights after dark 
			"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
			try:
				logger.info("is it time for nightlight?")
				self.nightlight()
			except Exception, e:
				logger.error("Failed to complete the nightlight block")
				logger.error("Traceback: "+str(e))					

			"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
			blocks to check only if armageddion is at home
			"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
			owner = utilities.User()
			owner.getDetails("armageddion")
			ishome = owner.state

			if (ishome == 'online'):
				"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
					block to blur out quips once in a while 
				"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
				try:
					logger.info("is it time for a smartass quip?")
					self.beSmart()
				except Exception, e:
					logger.error("Failed to complete the quip block")
					logger.error("Traceback: "+str(e))

				"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
					Block to check unread emails (gMail)
				"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
				try:
					logger.info("Checking Gmail")
					self.checkGmail()
				except Exception, e:
					logger.error("Failed to check Gmail")
					logger.error("Traceback: "+str(e))				

				"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
					Run morning alarm
				"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""				
				try:
					schedule.run_pending()
				except Exception, e:
					logger.error("Failed to check the morning alarm schedule")
					logger.error("Traceback: "+str(e))


			# OK Take a break 
			time.sleep(10)

	def checkGmail(self):
		"""
			Description:
				Checks the unread count in gMail
		"""
		global unread_Count
		global unread_Count_new

		try:
			unread_Count_new = utilities.getUnreadCount()
			logger.info("Gmail check successful")
		except Exception, e:
			logger.error("Gmail check failed")
			logger.error("Traceback "+str(e))

		if (unread_Count < unread_Count_new):
			logger.info("a new email has arrived")
			
			logger.info("Speaking email notification")
			emailQuips = [
			"Yet another email",
			"Pardon the interruption sir. Another email has arrived for you to ignore."]

			tempint = randint(1,len(emailQuips))
			utilities.speakString(emailQuips[tempint-1])

		if (unread_Count_new != 0):
			logger.info("unread Count: "+str(unread_Count_new))

		unread_Count = unread_Count_new
			
	def welcomeHome(self,time_away=None):
		"""
			Description:
				Speak a 'welcome home' greeting
		"""
		logger.info("Greeting the creator")
		
	def beSmart(self):
		"""
			Description:
				speak a quip
		"""
		global quipStartTime
		global waittime_quip

		if((int(time.strftime("%H", time.localtime()))>7)and(int(time.strftime("%H", time.localtime()))<22)):
			if(time.time()-quipStartTime>(waittime_quip*60)):
				logger.info("time to be a smart ass ")
				
				utilities.speakRandom()

				quipStartTime = time.time()
				waittime_quip = randint(10,50)
				print "Timme until next quip: ", waittime_quip
				logger.info("quipStartTime and waittime_quip have been reset")
				logger.info("next quip will be shouted in "+str(waittime_quip)+" minutes.")		

	def playTune(self):
		"""
			Description:
				pick a random song from current weather category and play it
		"""
		logger.info("playing a tune")

	def nightlight(self):
		"""
			Description:
				is anyone at home?
				it it after dark? 
				turn the lights on or off as needed. 
		"""		
		utilities.nighttime_auto()

def init_daemon():
	utilities.speakString("Initializing systems check")
	
	# initial geo check
	try:
		utilities.speakString("Running geo scan")
		logger.info("Running a geoscan")
		ret = utilities.getLocation("freegeoip")
		if not ret[0]:
			raise Exception("geoscan failed")
		utilities.speakString("geo scan complete")
	except Exception, e:
		utilities.speakString("Failed to complete geo scan")
		logger.error("Failed to complete geoscan scan")
		logger.error("Traceback: "+str(e))			
	
	#initial lighting check
	try:
		utilities.speakString("Running lighting check")
		logger.info("Running a lighting check")
		utilities.lightingInit()
		utilities.speakString("lighting check complete")
	except Exception, e:
		utilities.speakString("Failed to complete lighting check")
		logger.error("Failed to complete lighting check")
		logger.error("Traceback: "+str(e))

	#initial coffee check
	try:
		utilities.speakString("Looking for a source of coffee")
		logger.info("Running a coffee check")
		utilities.coffeeCheck()
		utilities.speakString("Brew check complete")
	except Exception, e:
		utilities.speakString("Failed to find a source of coffee")
		logger.error("Failed to complete coffee check")
		logger.error("Traceback: "+str(e))

	utilities.speakString("Systems check complete")

if __name__ == "__main__":
	daemon = MyDaemon('/var/run/alfr3ddaemon/alfr3ddaemon.pid',stderr='/dev/null')
	#daemon = MyDaemon('/var/run/alfr3ddaemon/alfr3ddaemon.pid',stderr='/dev/stderr')
	if len(sys.argv) == 2:
		if 'start' == sys.argv[1]:
			logger.info("Alfr3d Daemon initializing")
			init_daemon()
			logger.info("Alfr3d Daemon starting...")
			utilities.speakString("All systems are up and operational")
			daemon.start()
		elif 'stop' == sys.argv[1]:
			logger.info("Alfr3d Daemon stopping...")			
			daemon.stop()
		elif 'restart' == sys.argv[1]:
			daemon.restart()
		else:
			print "Unknown command"
			sys.exit(2)
		sys.exit(0)
	else:
		print "usage: %s start|stop|restart" % sys.argv[0]
		sys.exit(2)
