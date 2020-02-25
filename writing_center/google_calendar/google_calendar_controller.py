from datetime import datetime

from writing_center.db_repository import db_session
from writing_center.db_repository.tables import UserTable, AppointmentsTable


class GoogleCalendarController:
    def __init__(self):
        pass

    def handle_event(self, appt_id, service):
        appt = self.get_appointment_by_id(appt_id)
        start_time = appt.scheduledStart
        end_time = appt.scheduledEnd

        self.create_event(appt.id, start_time, end_time, service)

    def handle_events(self, user, page_type, service):
        if page_type == 'student':
            future_appts = self.get_future_user_appointments(user.id)
        else:
            future_appts = self.get_future_tutor_appts(user.id)

        for appt in future_appts:
            self.create_event(appt.id, appt.scheduledStart, appt.scheduledEnd, service)

    def create_event(self, appt_id, start_time, end_time, service):
        query = "Writing Center Appointment"
        events = service.events().list(calendarId='primary', q=query, singleEvents='True', orderBy='startTime',
                                       timeMin=datetime.now().strftime('%Y-%m-%dT%H:%M:%S-06:00'),
                                       showDeleted=True).execute()
        events = events.get('items')

        exists = False
        for event in events:
            try:
                if int(event['id']) == appt_id:
                    event['status'] = 'confirmed'
                    event['start']['dateTime'] = start_time.strftime('%Y-%m-%dT%H:%M:%S')
                    event['end']['dateTime'] = end_time.strftime('%Y-%m-%dT%H:%M:%S')
                    event = service.events().update(calendarId='primary', body=event, eventId=appt_id).execute()
                    exists = True
            except:
                pass

        if not exists:
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
                print(e)
                pass

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

    def get_future_tutor_appts(self, tutor_id):
        return db_session.query(AppointmentsTable)\
            .filter(AppointmentsTable.tutor_id == tutor_id)\
            .filter(AppointmentsTable.scheduledStart >= datetime.now())\
            .all()

    def credentials_to_dict(self, credentials):
        return {'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes}

