#!/usr/bin/python

"""
This file is used for all weather related functions.
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

import json											# used to handle jsons returned from www
import urllib										# used to make calls to www
import os											# used to allow execution of system level commands
import math											# used to round numbers
import logging										# needed for useful logs
import socket
import ConfigParser
from pymongo import MongoClient						# database link 
from time import gmtime, strftime, localtime		# needed to obtain time
from speak import speakString
from random import randint

# current path from which python is executed
CURRENT_PATH = os.path.dirname(__file__)

# set up logging 
logger = logging.getLogger("WeatherLog")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.FileHandler(os.path.join(CURRENT_PATH,"../log/weather.log"))
handler.setFormatter(formatter)
logger.addHandler(handler)

def getWeather(city="Toronto",country="CA"):
	"""
        Description:
            This function gets weather data and parses it. 
        Return:
            Boolean; True if successful, False if not.
    """
	# get API key for openWeather 
	logger.info("Getting weather data for "+city+", "+country)
	config = ConfigParser.RawConfigParser()
	config.read(os.path.join(os.path.dirname(__file__),'../conf/apikeys.conf'))
	apikey = config.get("API KEY", "openWeather")

	db_user = config.get("Alfr3d DB", "user")
	db_pass = config.get("Alfr3d DB", "password")

	weatherData = None

	url = "http://api.openweathermap.org/data/2.5/weather?q="+city+","+country+'&appid='+apikey
	try:
		weatherData = json.loads(urllib.urlopen(url).read().decode('utf-8'))
	except:
		logger.error("Failed to get weather data\n")	
		return False, weatherData

	logger.info("got weather data for "+city+", "+country)
	logger.info(weatherData)		# DEBUG

	#log current conditions
	logger.info("City:                           "+str(weatherData['name']))
	logger.info("Wind Speed:                     "+str(weatherData['wind']['speed']))
	logger.info("Atmospheric Pressure            "+str(weatherData['main']['pressure']))
	logger.info("Humidity                        "+str(weatherData['main']['humidity']))
	logger.info("Today's Low:                    "+str(KtoC(weatherData['main']['temp_min'])))
	logger.info("Today's High:                   "+str(KtoC(weatherData['main']['temp_max'])))
	logger.info("Description:                    "+str(weatherData['weather'][0]['description']))
	logger.info("Current Temperature:            "+str(KtoC(weatherData['main']['temp'])))
	logger.info("Sunrise:                        "+str(strftime('%H:%M', localtime(weatherData['sys']['sunrise']))))
	logger.info("Sunset:                         "+str(strftime('%H:%M', localtime(weatherData['sys']['sunset']))))

	logger.info("Parsed weather data\n")

	# Initialize the database
	client = MongoClient('mongodb://ec2-52-89-213-104.us-west-2.compute.amazonaws.com:27017/')
	client.Alfr3d_DB.authenticate(db_user,db_pass)
	db = client['Alfr3d_DB']
	collection_env = db['environment']	

	logger.info("Updating weather data in DB")
	collection_env.update({"name":socket.gethostname()},{"$set":{
						   "weather":{
							   "sunrise":str(weatherData['sys']['sunrise']),
							   "sunset":str(weatherData['sys']['sunset']),
							   "todays_high":str(KtoC(weatherData['main']['temp_max'])),
							   "todays_low":str(KtoC(weatherData['main']['temp_min']))}
						   }})


	# Subjective weather 
	badDay = []
	badDay_data = []
	badDay.append(False)
	badDay.append(badDay_data)

	# if weather is bad... 
	if weatherData['weather'][0]['main'] in ['Thunderstorm','Drizzle','Rain','Snow','Atmosphere','Exreeme']:
		badDay[0] = True
		badDay[1].append(weatherData['weather'][0]['description'])
	elif weatherData['main']['humidity'] > 65:
		badDay[0] = True
		badDay[1].append(weatherData['main']['humidity'])
	if KtoC(weatherData['main']['temp_max']) > 27:
		badDay[0] = True
		badDay[1].append(weatherData['main']['temp_max'])		
	elif KtoC(weatherData['main']['temp_min']) < -5:
		badDay[0] = True
		badDay[1].append(weatherData['main']['temp_min'])		
	if weatherData['wind']['speed'] > 10:
		badDay[0] = True
		badDay[1].append(weatherData['wind']['speed'])

	logger.info("Speaking weather data:\n")
	# Speak the weather data
	greeting = ''
	random = ["Weather patterns ", "My scans "]
	greeting += random[randint(0,len(random)-1)]	

	# Time variables
	hour=strftime("%I", localtime())
	minute=strftime("%M", localtime())
	ampm=strftime("%p",localtime())

	if badDay[0]:
		speakString("I am afraid I don't have good news.")
		greeting+="indicate "

		for i in range(len(badDay[1])):
			if badDay[1][i] == weatherData['weather'][0]['description']:
				greeting += badDay[1][i]
			elif badDay[1][i] == weatherData['main']['humidity']:
				greeting += "humidity of a steam bath"
			elif badDay[1][i] == weatherData['main']['temp_max']:
				greeting += "it is too hot for my gentle circuits"
			elif badDay[1][i] == weatherData['main']['temp_min']:
				greeting += "it is catalysmically cold"
			elif badDay[1][i] == weatherData['wind']['speed']:
				greeting += "the wind will seriously ruin your hair"

			if len(badDay[1])>=2 and i < (len(badDay[1])-1):
				add = [' , also, ',' , and if that isn\'t enough, ', ' , and to make matters worse, ']
				greeting += add[randint(0,len(add)-1)]
			elif len(badDay[1])>2 and i == (len(badDay[1])-1):
				greeting += " , and on top of everything, "
			else:
				logger.info(greeting+"\n")
		speakString(greeting)		
	else:
		speakString("Weather today is just gorgeous!")
		greeting += "indicate "+weatherData['weather'][0]['description']
		speakString(greeting)
		logger.info(greeting+"\n")

	speakString("Current temperature in "+weatherData['name']+" is "+str(KtoC(weatherData['main']['temp']))+" degrees")
	if (ampm=="AM" and int(hour)<10):
		speakString("Today\'s high is expected to be "+str(KtoC(weatherData['main']['temp_max']))+" degrees")

	logger.info("Spoke weather\n")
	return True

	f.close()

def KtoC(tempK):
	"""
		converts temperature in kelvin to celsius
	"""
	return math.trunc(int(tempK)-273.15)

# purely for testing purposes
if __name__ == "__main__":	
	getWeather()