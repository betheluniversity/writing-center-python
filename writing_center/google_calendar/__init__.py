from flask_classy import route, FlaskView, request
from flask import json, url_for, redirect
from flask import session as flask_session
from google.oauth2.credentials import Credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build

from writing_center import app
from writing_center.google_calendar.google_calendar_controller import GoogleCalendarController


class GoogleCalendarView(FlaskView):
    route_base = '/google-calendar'

    def __init__(self):
        self.gcc = GoogleCalendarController()

    @route('login-to-google-calendar', methods=['POST'])
    def login_to_google_calendar(self):
        login_page = str(json.loads(request.data).get('page_type'))
        flask_session['LOGIN-PAGE'] = login_page

        scopes = ['https://www.googleapis.com/auth/calendar.events']
        user = self.gcc.get_user_by_username(flask_session['USERNAME'])

        # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            app.config['GC_CLIENT_SECRET'], scopes=scopes)

        # The URI created here must exactly match one of the authorized redirect URIs
        # for the OAuth 2.0 client, which you configured in the API Console. If this
        # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
        # error.
        flow.redirect_uri = url_for('GoogleCalendarView:oauth2callback', _external=True)

        authorization_url, state = flow.authorization_url(
            # Enable offline access so that you can refresh an access token without
            # re-prompting the user for permission.
            access_type='offline',
            login_hint=user.email,
            prompt='consent',
            include_granted_scopes='true')

        # Store the state so the callback can verify the auth server response.
        flask_session['STATE'] = state

        return authorization_url

    @route("/add-google-calendar-event", methods=['POST'])
    def add_event_to_google_calendar(self):
        # Load credentials from the session.
        credentials = Credentials(
            **flask_session['CREDENTIALS'])

        service = build('calendar', 'v3', credentials=credentials, cache_discovery=False)

        appt_id = str(json.loads(request.data).get('appt_id'))

        self.gcc.handle_event(appt_id, service)

        return ''

    @route("/add-google-calendar-events", methods=['POST'])
    def add_events_to_google_calendar(self):
        # Load credentials from the session.
        credentials = Credentials(
            **flask_session['CREDENTIALS'])

        service = build('calendar', 'v3', credentials=credentials, cache_discovery=False)

        user = self.gcc.get_user_by_username(flask_session['USERNAME'])

        page_type = str(json.loads(request.data).get('page_type'))

        self.gcc.handle_events(user, page_type, service)

        return ''

    @route('/authorize')
    def authorize(self):
        scopes = ['https://www.googleapis.com/auth/calendar.events']
        user = self.gcc.get_user_by_username(flask_session['USERNAME'])

        # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            app.config['GC_CLIENT_SECRET'], scopes=scopes)

        # The URI created here must exactly match one of the authorized redirect URIs
        # for the OAuth 2.0 client, which you configured in the API Console. If this
        # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
        # error.
        flow.redirect_uri = url_for('GoogleCalendarView:oauth2callback', _external=True)

        authorization_url, state = flow.authorization_url(
            # Enable offline access so that you can refresh an access token without
            # re-prompting the user for permission.
            access_type='offline',
            login_hint=user.email,
            prompt='consent',
            include_granted_scopes='true')

        # Store the state so the callback can verify the auth server response.
        flask_session['STATE'] = state

        return redirect(authorization_url)

    def oauth2callback(self):
        scopes = ['https://www.googleapis.com/auth/calendar.events']
        # Specify the state when creating the flow in the callback so that it can
        # verified in the authorization server response.
        state = flask_session['STATE']

        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            app.config['GC_CLIENT_SECRET'],
            scopes=scopes,
            state=state)
        flow.redirect_uri = url_for('GoogleCalendarView:oauth2callback', _external=True)

        # Use the authorization server's response to fetch the OAuth 2.0 tokens.
        authorization_response = request.url

        flow.fetch_token(authorization_response=authorization_response)

        # Store credentials in the session.
        credentials = flow.credentials
        flask_session['CREDENTIALS'] = self.gcc.credentials_to_dict(credentials)

        login_page = flask_session['LOGIN-PAGE']
        if login_page == 'tutor':
            return redirect(url_for('SchedulesView:view_tutor_schedules'))
        elif login_page == 'student':
            return redirect(url_for('AppointmentsView:student_view_appointments'))
        else:
            return redirect(url_for('View:index'))



