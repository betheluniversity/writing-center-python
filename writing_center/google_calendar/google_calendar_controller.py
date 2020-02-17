from __future__ import print_function
import pickle
import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime


from writing_center.db_repository import db_session
from writing_center.db_repository.tables import UserTable, AppointmentsTable


class GoogleCalendarController:
    def __init__(self):
        pass

    def get_calendar_service(self):
        scopes = ['https://www.googleapis.com/auth/calendar.events']

        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.

        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'gc_client_secret.json', scopes)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        service = build('calendar', 'v3', credentials=creds)

        return service

    def handle_event(self, appt_id):
        service = self.get_calendar_service()

        appt = self.get_appointment_by_id(appt_id)
        start_time = appt.scheduledStart
        end_time = appt.scheduledEnd

        self.create_event(appt.id, start_time, end_time, service)

    def handle_events(self, user):
        service = self.get_calendar_service()

        future_appts = self.get_future_user_appointments(user.id)

        for appt in future_appts:
            self.create_event(appt.id, appt.scheduledStart, appt.scheduledEnd, service)

    def create_event(self, appt_id, start_time, end_time, service):
        query = "Writing Center Appointment"
        events = service.events().list(calendarId='primary', q=query, singleEvents='True', orderBy='startTime',
                                       timeMin=start_time.strftime('%Y-%m-%dT%H:%M:%S-06:00'),
                                       timeMax=end_time.strftime('%Y-%m-%dT%H:%M:%S-06:00')).execute()
        events = events.get('items')

        if events:
            try:
                event = service.events().delete(calendarId='primary', eventId=appt_id).execute()
            except:
                pass

        timezone = 'America/Chicago'

        event = {
            'id': appt_id,
            'summary': 'Writing Center Appointment',
            'location': 'Bethel University',
            'start': {
                'dateTime': start_time.strftime('%Y-%m-%dT%H:%M:%S'),
                'timeZone': timezone,
            },
            'end': {
                'dateTime': end_time.strftime('%Y-%m-%dT%H:%M:%S'),
                'timeZone': timezone,
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 10},
                ],
            },
            'Content-Type': 'application/json;charset=UTF-8',
        }

        try:
            event = service.events().insert(calendarId='primary', body=event).execute()
        except Exception as e:
            event = service.events().update(calendarId='primary', body=event, eventId=appt_id).execute()

    def get_appointment_by_id(self, appt_id):
        return db_session.query(AppointmentsTable)\
            .filter(AppointmentsTable.id == appt_id)\
            .one_or_none()

    def get_future_user_appointments(self, user_id):
        return db_session.query(AppointmentsTable)\
            .filter(AppointmentsTable.student_id == user_id)\
            .filter(AppointmentsTable.scheduledStart > datetime.now())\
            .all()

    def get_user_by_username(self, username):
        return db_session.query(UserTable)\
            .filter(UserTable.username == username)\
            .one_or_none()

