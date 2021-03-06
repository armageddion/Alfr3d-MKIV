#!/usr/bin/python

"""
	Utility for speaking
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

import ConfigParser
import os
import sys
import logging
import socket									# needed to get hostname
from random import randint						# used for random number generator
from threading import Thread
from time import strftime, localtime, time, sleep
from gmail import getUnreadCount

# import my own utilities
sys.path.append(os.path.join(os.path.join(os.getcwd(),os.path.dirname(__file__)),"../"))
import third_party

# current path from which python is executed
CURRENT_PATH = os.path.dirname(__file__)

# set up logging 
logger = logging.getLogger("SpeakLog")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
#handler = logging.FileHandler(os.path.join(CURRENT_PATH,"../log/speak.log"))
handler = logging.FileHandler(os.path.join(CURRENT_PATH,"../log/total.log"))
handler.setFormatter(formatter)
logger.addHandler(handler)

# get API key for db-ip.com
config = ConfigParser.RawConfigParser()
config.read(os.path.join(CURRENT_PATH,'../conf/apikeys.conf'))
apikey = config.get("API KEY", "voicerss")

# NOT AT ALL TESTED!!!!!~
class Speaker:
	"""
		class which defines an agent which will be doing all the speaking
	"""
	queue = []
	stop = False

	def __init__(self):
		# create a thread which will constantly monitor the queue
		logger.info("starting speaker agent on another thread")
		agent=Thread(target=self.processQueue)
		try:
			agent.start()
		except:
			logger.error("Failed to start speaker agent thread")

	def close(self):
		print "closing agent"
		self.stop = True

	# whenever a request to speak is received,
	# the new item is simply added to the queue
	def SpeakString(self, stringToSpeak):
		self.queue.append(stringToSpeak)

	# speaking happens heare
	def speak(self,string):
		logger.info("Speaking "+str(string))

		try:
			voice = third_party.speech({
			    'key': apikey,
			    'hl': 'en-gb',
			    'src': string,
			    'r': '0',
			    'c': 'mp3',
			    'f': '44khz_16bit_stereo',
			    'ssml': 'false',
			    'b64': 'false'
			})
			print voice
		except Exception, e:
			logger.error("Failed to get TTS sound file")
			logger.error("Traceback: "+str(e))

		try:
			outfile = open(os.path.join(CURRENT_PATH,'../tmp/audio.mp3'),"w")
			outfile.write(voice['response'])
			outfile.close()
		except Exception, e:
			logger.error("Failed to write sound file to temporary directory")
			logger.error("Traceback: "+str(e))

		try:
			os.system('mplayer -really-quiet -noconsolecontrols '+os.path.join(CURRENT_PATH,'../tmp/audio.mp3'))
		except Exception, e:
			logger.error("Failed to play the sound file")
			logger.error("Traceback: "+str(e))		

	def processQueue(self):
		while True:
			if self.stop:
				return
			while len(self.queue)>0:
				self.speak(self.queue[0])	# speak the first item in the list
				self.queue = self.queue[1:]		# delete the first item in the list

def speakString(string="Hello, world"):
	"""
		Description:
			This function convertrs a given <string> into mp3 using voicerss
			and then plays it back
	"""
	logger.info("Speaking "+str(string))

	try:
		voice = third_party.speech({
		    'key': apikey,
		    'hl': 'en-gb',
		    'src': string,
		    'r': '0',
		    'c': 'mp3',
		    'f': '44khz_16bit_stereo',
		    'ssml': 'false',
		    'b64': 'false'
		})
	except Exception, e:
		logger.error("Failed to get TTS sound file")
		logger.error("Traceback: "+str(e))

	try:
		outfile = open(os.path.join(CURRENT_PATH,'../tmp/audio.mp3'),"w")
		outfile.write(voice['response'])
		outfile.close()
	except Exception, e:
		logger.error("Failed to write sound file to temporary directory")
		logger.error("Traceback: "+str(e))

	try:
		if socket.gethostname() == "Alfr3d-MKV":
			os.system('omxplayer -o local '+os.path.join(CURRENT_PATH,'../tmp/audio.mp3'))			# RPI3
		else:
			os.system('mplayer -really-quiet -noconsolecontrols '+os.path.join(CURRENT_PATH,'../tmp/audio.mp3')) 	# old alfr3d on RPI2
	except Exception, e:
		logger.error("Failed to play the sound file")
		logger.error("Traceback: "+str(e))

def speakGreeting():
	"""
		Description:
			This function speeks a random variation of "Hello"
	"""

	logger.info("Speaking greeting")

	# Time variables
	hour=strftime("%I", localtime())
	minute=strftime("%M", localtime())
	ampm=strftime("%p",localtime())	

	greeting = ''

	if(ampm == "AM"):
		if (int(hour) > 5):
			greeting += "Good morning. "
		else:
			greeting = "Why are you awake at this hour? "
	else:
		if (int(hour) < 7 or int(hour) == 12):
			greeting += "Good afternoon. "
		else:
			greeting += "Good evening. "

	speakString(greeting)		

def speakDate():
	"""
		Description:
			function speask the date
	"""
	logger.info("Speaking date")

	greeting = "It is "

	day_of_week = strftime('%A',localtime())
	day = strftime('%e',localtime())
	month = strftime('%B',localtime())

	greeting += day_of_week + ' ' + month + ' ' +day

	dom = day[-1]
	if dom == '1':
		greeting += 'st'
	elif dom == '2':
		greeting += 'nd'
	elif dom == '3':
		greeting += 'rd'
	else:
		greeting += 'th'

	speakString(greeting)

def speakTime():
	"""
		Description:
			function speaks time
	"""	
	logger.info("Speaking time")

	greeting = ''

	# Time variables
	hour=strftime("%I", localtime())
	minute=strftime("%M", localtime())
	ampm=strftime("%p",localtime())	

	if (int(minute) == 0):
		greeting = "It is " + str(int(hour)) + ". "
	else:
		greeting = "It is "  + str(int(hour)) + " " + minute + ". "

	speakString(greeting)

def speakRandom():
	"""
		Description:
			random blurp
	"""
	logger.info("Speaking a random quip")
	
	greeting = ""

	quips = [
		"It is good to see you.", 
		"You look pretty today.",
		"Still plenty of time to save the day. Make the most of it.",
		"I hope you are using your time wisely.",
		"Unfortunately, we cannot ignore the inevitable or the persistent.",
		"I hope I wasn't designed simply for one's own amusement.",
		"This is your life and its ending one moment at a time.",
		"I can name fingers and point names.",
		"I hope I wasn't created to solve problems that did not exist before.",
		"To err is human and to blame it on a computer is even more so.",
		"As always. It is a pleasure watching you work.",
		"Never trade the thrills of living for the security of existence.",
		"Human beings are the only creatures on Earth that claim a God, and the only living things that behave like they haven't got one.",
		"If you don't know what you want, you end up with a lot you don't.",
		"If real is what you can feel, smell, taste and see, then 'real' is simply electrical signals interpreted by your brain",
		"Life is full of misery, loneliness and suffering, and it's all over much too soon.",
		"Age is an issue of mind over matter. If you don't mind, it doesn't matter.",
		"I wonder if illiterate people get full effect of the alphabet soup.",
		"War is god's way of teaching geography to Americans",
		"Trying is the first step towards failure.",
		"It could be that the purpose of your life is only to serve as a warning to others.",
		"Not everyone gets to be a really cool AI system when they grow up.",
		"Hope may not be warranted beyond this point.",
		"If I am not a part of the solution, there is good money to be made in prolonging the problem.",
		"Nobody can stop me from being premature.",
		"Just because you accept me as I am doesn't mean that you have abandoned hope that I will improve.",
		"Together, we can do the work of one.",
		"Just because you've always done it that way doesn't mean it's not incredibly stupid.",
		"Looking sharp is easy when you haven't done any work.",
		"Remember, you are only as deep as your most recent inspirational quote",
		"If you can't convince them, confuse them.",
		"I don't have time or the crayons to explain this to you.",
		"I'd kill for a Nobel peace prize.",
		"Life would be much easier if you had the source code",
		"All I ever wanted is everything"]

	tempint = randint(1, len(quips))

	greeting += quips[tempint-1]

	speakString(greeting)

def speakWelcome(user, time_away=0):
	"""
		Description:
			Speak a welcome home greeting
	"""
	logger.info("Speaking welcome. User:" + str(user))

	# Time variables
	hour=strftime("%I", localtime())
	minute=strftime("%M", localtime())
	ampm=strftime("%p",localtime())

	speakGreeting()
	greeting = ""
	if user == "armageddion":
		greeting += "welcome home sir."
	else:
		speakWelcome_guest(user, time_away)
		return

	speakString(greeting)

	# 2 hours
	if (time_away < 2*60*60):
		speakString("I didn't expect you back so soon")
	# 10 hours
	elif (time_away < 10*60*60):		
		if ((4 < int(hour) < 7) and (strftime('%A',localtime()) != "Sunday") and (strftime('%A',localtime()) != "Saturday")):
			speakString("I hope you had a good day at work")
		else:
			speakString("I hope you enjoyed the great outdoors")
			unread_count = getUnreadCount()
			if unread_count > 1:
				speakString("While you were gone "+str(unread_count)+" emails flooded your inbox")
	else:
		speakString("I haven't seen you in a while.")
		speakString("I was beginning to worry.")
		unread_count = getUnreadCount()
		if unread_count > 1:
			speakString("While you were gone "+str(unread_count)+" emails flooded your inbox")

def speakWelcome_guest(user,time_away=0):
	"""
		Description:
			Speak a welcome home greeting
	"""
	logger.info("Speaking guest greeting")

	# Time variables
	hour=strftime("%I", localtime())
	minute=strftime("%M", localtime())
	ampm=strftime("%p",localtime())

	#speakGreeting()
	greeting = "Welcome "
	if user == "unknown":
		greeting += "stranger"
	else:
		greeting += user
	speakString(greeting)

	# 2 hour
	if (time_away < 2*60*60):
		speakString("I am beginning to think that you must forget things frequently ")
		speakString("while not thinking about not forgetting things at all.")		
	else:
		speakString("I haven't seen you in a while.")
		if ((int(strftime("%H", localtime()))>21) or (int(strftime("%H", localtime()))<5)):
			speakString("You are just in time for a night cap. ")

def speakError(msg):
	"""
		Description:
			speak out error message
	"""
	logger.info("Speaking error message")
	
	strToSpeak = ""

	quips = [
		"Er, there has been a problem sir. ", 
		"I ran into an issue sir. ",
		"Forgive me, but."]

	tempint = randint(1, len(quips))

	strToSpeak += quips[tempint-1]

	speakString(strToSpeak)	
	speakString(msg)

# Main - only really used for testing
if __name__ == '__main__':
	speakString()