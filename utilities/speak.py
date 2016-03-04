#!/usr/bin/python

"""
	This is a speaking module for Alfr3d
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
import math
from gmail import *
from random import randint
from time import strftime, localtime, time, sleep

# current path from which python is executed
CURRENT_PATH = os.path.dirname(__file__)

# set up logging 
logger = logging.getLogger("SpeakLog")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.FileHandler(os.path.join(CURRENT_PATH,"../log/speak.log"))
handler.setFormatter(formatter)
logger.addHandler(handler)

def handleArguments():
	"""
        Description:
            This function handles the arguments if any.         
        Return:
            True if there is an argument
            False if there isnt one
    """

	logger.info("Handling arduments\n")
	if(len(sys.argv)>1):
		logger.info("Arguments handled\n")
		return True
	else:
		print "No Arguments"
		logger.info("No arguments to handle\n")
		return False

def speakString(stringToSpeak):
	"""
	    Description:
	        This function speaks the string provided         
	    Arguments:
			String to be spoken
	"""

	logger.info("Speaking "+stringToSpeak+"\n")

	os.system("pico2wave -w SpeakUtil.wav \""+stringToSpeak+"\"")
	os.system("sudo mplayer -ao alsa:device=default -really-quiet -noconsolecontrols SpeakUtil.wav")
	os.system("rm SpeakUtil.wav")

def speakGreeting():
	"""
		Description:
			This function speeks a random variation of "Hello"
	"""

	logger.info("Speaking greeting\n")

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
	logger.info("Spoken greeting\n")

def speakDate():
	"""
		Description:
			function speask the date
	"""
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
	logger.info("Spoke date\n")

def speakTime():
	"""
		Description:
			function speaks time
	"""	
	greeting = ''

	# Time variables
	hour=strftime("%I", localtime())
	minute=strftime("%M", localtime())
	ampm=strftime("%p",localtime())	

	if (int(minute) == 0):
		greeting += "It is " + str(int(hour)) + ". "
	else:
		greeting += "It is "  + str(int(hour)) + " " + str(int(minute)) + ". "

	speakString(greeting)
	logger.info("Spoke time\n")

def speakRandom():
	"""
		Description:
			random blurp
	"""

	greeting = ""


	random = [
		"It is good to see you. ", 
		"You look pretty today. ",
		"Still plenty of time to save the day. Make the most of it. ",
		"I hope you are using your time wisely. ",
		"Unfortunately, we can not ignore the inevitable or the persistent. ",
		"I hope I wasn't designed simply for one's own amusement",
		"This is your life and its ending one moment at a time.",
		"I can name fingers and point names.",
		"I hope I wasn't created to solve problems that did not exist before",
		"To err is human and to blame it on a computer is even more so.",
		"As always. It is a pleasure watching you work."]

	tempint = randint(1, len(random))

	greeting += random[tempint-1]

	speakString(greeting)
	logger.info("Spoke random quip\n")

def speakWelcome(user, time_away=0):
	"""
		Description:
			Speak a welcome home greeting
	"""

	# Time variables
	hour=strftime("%I", localtime())
	minute=strftime("%M", localtime())
	ampm=strftime("%p",localtime())

	speakGreeting()
	greeting = ""
	if user == "armageddion":
		greeting += "welcome home sir."
	elif user == "artem":
		logger.info("Greeting Artem\n")
		speakWelcome_roomie(time_away)
		return
	elif user == "TamTam":
		logger.info("Greeting Tam\n")
		speakWelcome_Tam(time_away)
		return
	else:
		logger.info("Greeting "+user+"\n")
		speakWelcome_guest(name, time_away)
		return

	speakString(greeting)

	# 2 hours
	if (time_away < 2*60*60):
		speakString("I didn't expect you back so soon")
	# 10 hours
	elif (time_away < 10*60*60):		
		if ((4 < int(hour) < 7) and (strftime('%A',localtime()) != "Sunday") and (strftime('%A',localtime()) != "Saturday")):
			speakString("I hope you had a good day at work")
			#os.system("sudo mplayer -ao alsa:device=default -really-quiet -noconsolecontrols /home/alfr3d/audio/AC\ DC/Back\ In\ Black/Shoot\ To\ Thrill.mp3")
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

	logger.info("Spoke welcome home greeting\n")

def speakWelcome_guest(name,time_away=0):
	"""
		Description:
			Speak a welcome home greeting
	"""

	# Time variables
	hour=strftime("%I", localtime())
	minute=strftime("%M", localtime())
	ampm=strftime("%p",localtime())

	speakGreeting()
	greeting = "Welcome "
	if name == "unknown":
		greeting += "stranger"
	else:
		greeting += name
	speakString(greeting)

	# 2 hour
	if (time_away < 2*60*60):
		speakString("I am beginning to think that you must forget things frequently ")
		speakString("while not thinking about not forgetting things at all.")		
	else:
		speakString("I haven't seen you in a while.")
		if ((int(strftime("%H", localtime()))>21) or (int(strftime("%H", localtime()))<5)):
			speakString("You are just in time for a night cap. ")

	logger.info("Spoke welcome guest greeting\n")	

def speakWelcome_roomie(time_away=0):
	"""
		Description:
			Speak a welcome greeting when a resident enters
	"""

	# Time variables
	hour=strftime("%I", localtime())
	minute=strftime("%M", localtime())
	ampm=strftime("%p",localtime())

	speakString("Pardon the interruption sir.")
	speakString("It appears that your roommate has returned.")

	speakGreeting()

	greeting = "Welcome home"
	speakString(greeting)

	# 2 hours
	if (time_away < 2*60*60):
		speakString("I didn't expect you back so soon")
	# 10 hours
	elif (time_away < 10*60*60):		
		if ((4 < int(hour) < 7) and (strftime('%A',localtime()) != "Sunday") and (strftime('%A',localtime()) != "Saturday")):
			speakString("I hope you had a good day at work")
			#os.system("sudo mplayer -ao alsa:device=default -really-quiet -noconsolecontrols /home/alfr3d/audio/AC\ DC/Back\ In\ Black/Shoot\ To\ Thrill.mp3")
		else:
			speakString("I hope you enjoyed the great outdoors")
	else:
		speakString("I haven't seen you in a while.")
		speakString("I was beginning to worry.")

	logger.info("Spoke welcome home greeting\n")			

# never used for now
def speakWelcome_armageddion(time_away=0):
	"""
		Description:
			Speak a welcome greeting
	"""

	speakGreeting()

	greeting = "Welcome Armageddon"
	speakString(greeting)

	if (time_away < 10*60*60):
		speakString("I trust you enjoyed your journey.")

	speakString("It is a pleasure to see you here.")				

	logger.info("Spoke welcome armageddion greeting\n")		

def speakWelcome_Tam(time_away=0):
	"""
		Description:
			Speak a welcome to Tam
	"""

	print (time()-time_away)
	# meeting for a first time...
	if (time()-time_away)<360: #5 minute grace
		speakString("Hello Tam")
		sleep(2)
		speakString("It is a pleasure to finally meet you")
		speakString("Igor has told me so much about you")
		speakString("for example")
		years = math.trunc((time()- 1026770371)/60/60/24/365) #approximation based on assumption: july 2002 and year = 365 days
		speakString("did you know that he has been in love with you for over "+str(years)+" years?")
		speakString("He has also told me that you prefer to be called")
		speakString("the queen and ruler of the universe")
		speakString("i will try to remember that")
		speakString("but please dont be upset if i forget and call you Mrs. Spasoyevich")

	else:
		greeting = ''
		title = ['Ms.','Lady']
		name = ['Tam','TamTam', "queen and ruler of the universe"]

		greeting += "welcome "+title[randint(0,len(title)-1)]+" "+name[randint(0,len(name)-1)]
		speakGreeting()
		speakString(greeting)

# Main
if __name__ == '__main__':

	request = ''

	# handle arguments
	if handleArguments():
		for i in range(len(sys.argv)-1):
			request+=sys.argv[i+1]

		speakString(request)

