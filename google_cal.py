"""Google Calendar Class Object."""
from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


class google_cal:
    """Host Google Calendar object."""

    def __init__(self):
        """Initialize Calendar variables."""
        # If modifying these scopes, delete the file token.pickle.
        self.SCOPES = ['https://www.googleapis.com/auth/calendar']
        self.service = None
        self.event_dates = []

    def build(self):
        """Build/Authenticate Calendar."""
        creds = None
        # token.pickle stores user's access and refresh tokens, created
        # automatically when authorization flow completes.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('calendar', 'v3', credentials=creds)
        print('Calendar Built')

    def week_events(self, cal_id, date):
        """Get upcoming events for the week."""
        # Get start/end of the week
        monday = date - datetime.timedelta(days=date.weekday())
        sunday = monday + datetime.timedelta(days=7)
        monday = monday.isoformat() + 'Z'  # 'Z'indicates UTC
        sunday = sunday.isoformat() + 'Z'  # 'Z'indicates UTC

        print('Getting the upcoming ' + str() + ' events')
        events_result = self.service.events().list(
            calendarId=cal_id,
            timeMin=monday,
            timeMax=sunday,
            singleEvents=True,
            orderBy='startTime'
            ).execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
            if start.split('T')[0] not in self.event_dates:
                self.event_dates.append(start.split('T')[0])

    def get_event_dates(self):
        """Return all events collected."""
        return self.event_dates

    def add_event(self, cal_id, date, summary, startTime, endTime, desc):
        """Add event to Calendar."""
        event = {
          'summary': summary,
          'location': '',
          'description': desc,
          'start': {
            'dateTime': date + 'T' + startTime,
            'timeZone': 'America/Denver',
          },
          'end': {
            'dateTime': date + 'T' + endTime,
            'timeZone': 'America/Denver',
          },
          'recurrence': [],
          'attendees': [],
          'reminders': {
            'useDefault': True,
            'overrides': [],
          },
        }

        event = self.service.events().insert(
            calendarId=cal_id,
            body=event).execute()
        print('Event created: %s' % (event.get('htmlLink')))
