from flask_classy import route, FlaskView, request
from flask import json
from flask import session as flask_session


from writing_center.google_calendar.google_calendar_controller import GoogleCalendarController


class GoogleCalendarView(FlaskView):

    def __init__(self):
        self.gcc = GoogleCalendarController()

    @route("/add-google-calendar-event", methods=['POST'])
    def add_event_to_google_calendar(self):
        appt_id = str(json.loads(request.data).get('appt_id'))

        self.gcc.handle_event(appt_id)

        return ''

    @route("/add-google-calendar-events", methods=['POST'])
    def add_events_to_google_calendar(self):
        user = self.gcc.get_user_by_username(flask_session['USERNAME'])

        self.gcc.handle_events(user)

        return ''
