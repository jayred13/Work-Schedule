import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

class GCalanderHelper:
    def __init__(self, cal_id):
        self.cal_id = cal_id

    def authenticate(self):
        # If modifying these scopes, delete the file token.pickle.
        SCOPES = ['https://www.googleapis.com/auth/calendar']
        creds = None
        # # The file token.pickle stores the user's access and refresh tokens,
        # and is created automatically when the authorization flow completes
        # for the first time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        global service
        service = build('calendar', 'v3', credentials=creds)

    def upcoming_events(self, num):
        # Get start of the week
        now = datetime.datetime.utcnow()
        monday = now - datetime.timedelta(days=now.weekday())
        monday = monday.isoformat() + 'Z'  # 'Z'indicates UTC

        print('Getting the upcoming ' + str(num) + ' events')
        events_result = service.events().list(
            calendarId=self.cal_id,
            timeMin=monday, maxResults=num, singleEvents=True,
            orderBy='startTime'
            ).execute()
        events = events_result.get('items', [])
        return events

    def add_event(self, date, dept, startTime, endTime, changeDate):
        event = {
          'summary': dept,
          'description': 'Changed On:' + changeDate,
          'start': {
            'dateTime': date + 'T' + startTime,
            'timeZone': 'America/Chicago',
          },
          'end': {
            'dateTime': date + 'T' + endTime,
            'timeZone': 'America/Chicago',
          },
        }
        print("Adding..." + event['start'].get('dateTime'))

        event = service.events().insert(
            calendarId=self.cal_id,
            body=event).execute()
        print('Event created: %s' % (event.get('htmlLink')))

    def delete_event(self, event):
        print("Deleting..." + event['start'].get('dateTime'))
        eventId = event['id']
        service.events().delete(calendarId=self.cal_id, eventId=eventId).execute()

    def event_exists(self, events, date):
        for event in events:
            if str(date) in event['start'].get('dateTime'):
                return event
        return False
