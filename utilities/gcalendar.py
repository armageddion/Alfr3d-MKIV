#!/usr/bin/python

"""
This is a gmail API utility
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


from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime
import time

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = os.path.join(os.path.join(os.getcwd(),os.path.dirname(__file__)),'../conf/client_secret_calendar.json')
APPLICATION_NAME = 'Alfr3d'

# calculate offset to UTC
timezone_offset_int = int(time.strftime('%H',time.localtime()))-int(time.strftime('%H',time.gmtime()))
if abs(timezone_offset_int) < 10:
    if timezone_offset_int < 0:
        timezone_offset = "-0"+str(abs(timezone_offset_int))+":00"
    else:
        timezone_offset = "+0"+str(abs(timezone_offset_int))+":00"
else:
    timezone_offset = str(timezone_offset_int)+":00"

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    # credential_dir = os.path.join(home_dir, '.credentials')
    credential_dir = os.path.join(os.path.dirname(__file__),'../conf')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar.storage')
    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    eventsResult = service.events().list(
        calendarId='primary', timeMin=now, maxResults=10, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])

def calendar_today():
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    now = datetime.datetime.now().isoformat()+timezone_offset
    midnight = datetime.datetime.now().replace(hour=23,minute=59).isoformat()+timezone_offset
    print('Getting the all remaining events of today')
    eventsResult = service.events().list(
        calendarId='primary', timeMin=now, timeMax=midnight, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary']) 

def calendar_tomorrow():   
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    tomorrow = datetime.datetime.now().replace(hour=0,minute=0) + datetime.timedelta(days=1)
    tomorrow_night = tomorrow + datetime.timedelta(hours=23, minutes=59)
    tomorrow = tomorrow.isoformat()+timezone_offset
    tomorrow_night = tomorrow_night.isoformat()+timezone_offset
    
    print('Getting the first event of tomorrow')
    eventsResult = service.events().list(
        calendarId='primary', timeMin=tomorrow, maxResults=1, timeMax=tomorrow_night, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary']) 

        # since there is only one event, we're ok to do this
        return event

if __name__ == '__main__':
    main()
    print("\n")
    calendar_today()
    print("\n")
    calendar_tomorrow()