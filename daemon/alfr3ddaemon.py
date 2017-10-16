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
import datetime									
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
config.read(os.path.join(CURRENT_PATH,'../conf/apikeys.conf'))
# get main DB credentials
db_user = config.get("Alfr3d DB", "user")
db_pass = config.get("Alfr3d DB", "password")

# gmail unread count
unread_Count = 0
unread_Count_new = 0

# time of sunset/sunrise - defaults
sunset_time = datetime.datetime.now().replace(hour=19, minute=0)
sunrise_time = datetime.datetime.now().replace(hour=6, minute=30)
bed_time = datetime.datetime.now().replace(hour=23, minute=00)

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
				utilities.speakError("I failed to complete the network scan")
				logger.error("Traceback: "+str(e))			

			"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
				Send a report out
			"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""				
			try:
				logger.info("Creating a system report")
				reporting.sendReport()
			except Exception, e:
				logger.error("Failed to send report")
				utilities.speakError("I failed to send out status report")
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
					logger.info("Is it time for a smartass quip?")
					self.beSmart()
				except Exception, e:
					logger.error("Failed to complete the quip block")
					utilities.speakError("I failed in being a smart arse")
					logger.error("Traceback: "+str(e))

				"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
					Block to check unread emails (gMail)
				"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
				try:
					logger.info("Checking Gmail")
					self.checkGmail()
				except Exception, e:
					logger.error("Failed to check Gmail")
					utilities.speakError("I have been unable to check your mail")
					logger.error("Traceback: "+str(e))				

				"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
					Run morning alarm
				"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""				
				try:
					logger.info("Checking on scheduled jobs")
					schedule.run_pending()
				except Exception, e:
					logger.error("Failed to check the scheduled jobs")
					utilities.speakError("I failed to check your schedule")
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

		unread_Count_new = utilities.getUnreadCount()

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

def sunriseRoutine():
	"""
		Description:
			sunset routine - perform this routine 30 minutes before sunrise
			giving the users time to go see sunrise
			### TO DO - figure out scheduling
	"""		
	logger.info("Pre-sunrise routine")

	try:
		utilities.sunriseAlarm()
	except Exception, e:
		logger.error("Failed to complete pre-sunrise routine")
		logger.error("Traceback: "+str(e))	

	return schedule.CancelJob
	# if above fails try:
	#schedule.clear('sunrise-routine')
	#return							

def morningRoutine():
	"""
		Description:
			perform morning routine - ring alarm, speak weather, check email, etc..
	"""	
	logger.info("Time for morning routine")

	# ring morning alarm
	logger.info("Morning Alarm")
	try:
		utilities.smartAlarm()
	except Exception, e:
		logger.error("Failed to run morning alarm")
		utilities.speakError("Morning Alarm didn't work too well")
		logger.error("Traceback: "+str(e))			

	# check time of sunset and schedule evening lighting
	logger.info("Getting sunset data")
	global sunset_time

	client = MongoClient('mongodb://ec2-52-89-213-104.us-west-2.compute.amazonaws.com:27017/')
	client.Alfr3d_DB.authenticate(db_user,db_pass)
	db = client['Alfr3d_DB']	

	envCollection = db['environment']

	env = envCollection.find_one({"name":socket.gethostname()})
	try:
		sunset = int(env['weather']['sunset'])
		sunset_time = datetime.datetime.now().replace(hour=int(time.strftime('%H',time.localtime(sunset))), 
													  minute=int(time.strftime("%M",time.localtime(sunset)))
													  	)	
	except Exception, e:
		logger.error("Failed to find out the time of sunset")
		utilities.speakError("I have no idea when the sun will set")
		logger.error("Traceback: "+str(e))						

	try:
		schedule.every().day.at(str(sunset_time.hour)+":"+str(sunset_time.minute)).do(sunsetRoutine).tag("sunset-routine")
	except Exception, e:
		logger.error("Failed to create sunset schedule")
		utilities.speakError("I haven't been able to create sunset schedule")
		logger.error("Traceback: "+str(e))						

	# find out first calendar event tomorrow and schedule bedime
	logger.info("Getting calendar data for tomorrow")
	global bed_time

	try:
		event_tomorrow = utilities.calendarTomorrow()
		event_tomorrow_title = event_tomorrow['summary']
		event_tomottow_time = datetime.datetime.strptime( event_tomorrow['start'].get('dateTime').split("T")[1][:-6][:5], '%H:%M') 	# really complicated way to strip the returned date/time into just time and convert into datetime object..
	
		bed_time = event_tomottow_timen - datetime.timedelta(hours=9, minutes=0)
	except Exception, e:
		logger.error("Failed to check calendar")
		utilities.speakError("I haven't been able to get calendar info from google")
		logger.error("Traceback: "+str(e))			

	try:
		schedule.every().day.at(str(bed_time.hour)+":"+str(bed_time.minute)).do(bedtimeRoutine).tag("bedtime-routine")
	except Exception, e:
		logger.error("Failed to create bedtime schedule")
		utilities.speakError("I have been unable to create bedtime schedule")
		logger.error("Traceback: "+str(e))

def sunsetRoutine():
	"""
		Description:
			routine to perform at sunset - turn on ambient lights
	"""
	logger.info("Time for sunset routine")
	try:
		utilities.nighttime_auto()
	except Exception, e:
		logger.error("Failed to complete sunset routine")
		utilities.speakError("Sunset routine failed somewhere")
		logger.error("Traceback: "+str(e))			

	return schedule.CancelJob
	# if above fails try:
	#schedule.clear('sunset-routine')
	#return

def bedtimeRoutine():
	"""
		Description:
			routine to perform at bedtime - turn on ambient lights
	"""
	logger.info("Bedtime")
	try:
		utilities.lightingOff()
		utilities.smartAlarm()
	except Exception, e:
		logger.error("Failed to complete bedtime routine")
		utilities.speakError("Bedtime routine didn't complete successfully")
		logger.error("Traceback: "+str(e))

	# get sunrise info 
	# and create a schedule for sunrise activities.. 
	logger.info("Getting sunrise data")
	global sunrise_time

	client = MongoClient('mongodb://ec2-52-89-213-104.us-west-2.compute.amazonaws.com:27017/')
	client.Alfr3d_DB.authenticate(db_user,db_pass)
	db = client['Alfr3d_DB']	

	envCollection = db['environment']

	env = envCollection.find_one({"name":socket.gethostname()})
	try:
		sunrise = int(env['weather']['sunrise'])-30*60 ## sunrise time minus 30 minutes
		sunrise_time = datetime.datetime.now().replace(hour=int(time.strftime('%H',time.localtime(sunrise))), 
													  minute=int(time.strftime("%M",time.localtime(sunrise)))
													  	)	
	except Exception, e:
		logger.error("Failed to find out the time of sunrise")
		utilities.speakError("I have no idea when the sun will rise")
		logger.error("Traceback: "+str(e))						
		return

	try:
		schedule.every().day.at(str(sunrise_time.hour)+":"+str(sunrise_time.minute)).do(sunriseRoutine).tag("sunrise-routine")
	except Exception, e:
		logger.error("Failed to create sunrise schedule")
		logger.error("Traceback: "+str(e))						

	return schedule.CancelJob
	# if above fails try:
	#schedule.clear('bedtime-routine')
	#return				

def init_daemon():
	"""
		Description:
			initialize alfr3d services 
	"""
	utilities.speakString("Initializing systems check")

	faults = 0
	
	# initial geo check
	try:
		utilities.speakString("Running geo scan")
		logger.info("Running a geoscan")
		ret = utilities.getLocation("freegeoip")
		if not ret[0]:
			raise Exception("Geo scan failed")
		utilities.speakString("Geo scan complete")
	except Exception, e:		
		utilities.speakString("Failed to complete geo scan")
		logger.error("Failed to complete geoscan scan")
		logger.error("Traceback: "+str(e))			
		faults+=1												# bump up fault counter
	
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
		faults+=1												# bump up fault counter		

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
		faults+=1												# bump up fault counter		

	# set up some routine schedules
	try: 
		utilities.speakString("Setting up scheduled routines")
		logger.info("Setting up scheduled routines")		
		schedule.every().day.at("8:30").do(morningRoutine)
		#schedule.every().day.at(str(bed_time.hour)+":"+str(bed_time.minute)).do(bedtimeRoutine)
	except Exception, e:
		utilities.speakString("Failed to set schedules")
		logger.error("Failed to set schedules")
		logger.error("Traceback: "+str(e))
		faults+=1												# bump up fault counter		

	utilities.speakString("Systems check complete")
	return faults

if __name__ == "__main__":
	daemon = MyDaemon('/var/run/alfr3ddaemon/alfr3ddaemon.pid',stderr='/dev/null')
	#daemon = MyDaemon('/var/run/alfr3ddaemon/alfr3ddaemon.pid',stderr='/dev/stderr')
	if len(sys.argv) == 2:
		if 'start' == sys.argv[1]:
			logger.info("Alfr3d Daemon initializing")
			faults = init_daemon()
			logger.info("Alfr3d Daemon starting...")
			if faults != 0:
				utilities.speakString("Some faults were detected but system started successfully")
				utilities.speakString("Total number of faults is "+str(faults))
			else:
				utilities.speakString("All systems are up and operational")
			morningRoutine()
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
