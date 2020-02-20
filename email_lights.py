#Written by Jeremy Jung (May 22 2019)
#Connects to any gmail account and sees if any unread emails exist.
#The gmail account must allow interaction with Gmail API
#A hardware that is a physical mailbox with LED lights is connected
#via GPIO to the raspberry pi. Lights flash on and off when there
#are unread emails, otherwise the lights do not flash.
from __future__ import print_function
import pickle
import os.path
import RPi.GPIO as GPIO, feedparser, time, os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

#initialize the GPIO pin variable. The LIGHTS var can change to any PIN connected to the LED lights
GPIO.setmode(GPIO.BCM)
LIGHTS = 18
GPIO.setup(LIGHTS, GPIO.OUT)

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def main():
    #sets up the token of Gmail account
    creds = None
    if os.path.exists('/home/pi/token.pickle'):
        with open('/home/pi/token.pickle','rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        with open('/home/pi/token.pickle','wb') as token:
            pickle.dump(creds,token)
    service = build('gmail','v1',credentials=creds)
    #get the unread emails roster
    results = service.users().messages().list(userId='me', labelIds = 'UNREAD',maxResults = 110).execute()
    #get all unread emails objects
    msgs = results.get('messages',[])
    #don't flash lights there is no unread email
    if not msgs:
        print('No msgs found')
        GPIO.output(LIGHTS, False)
    #flash lights when there is unread email
    else:
        print('msgs:')
        unread_msgs = 0
        for msg in msgs:
            print(msg)
            unread_msgs +=1
        print("Total of " + str(unread_msgs) + " unread_messages")
        if unread_msgs > 0:
            GPIO.output(LIGHTS, True)
            time.sleep(0.4)
            GPIO.output(LIGHTS, False)
            time.sleep(0.4)

#execute the main function
if __name__ == '__main__':
    while True:
        main()
