import logging

from flask import Flask, request
from flask import session as flask_session
from datetime import datetime
from raven.contrib.flask import Sentry

app = Flask(__name__)
app.config.from_object('config')

from writing_center.db_repository import db_session

# sentry = Sentry(app, dsn=app.config['SENTRY_URL'], logging=True, level=logging.INFO)
# if app.config['ENVIRON'] == 'prod':
#     from writing_center import error

# Declaring and registering the views
from writing_center.views import View
from writing_center.message_center import MessageCenterView
from writing_center.appointments import AppointmentsView
from writing_center.cron import CronView
from writing_center.profile import ProfileView
from writing_center.schedules import SchedulesView
from writing_center.settings import SettingsView
from writing_center.statistics import StatisticsView
from writing_center.users import UsersView
from writing_center.users.users_controller import UsersController as uc
from writing_center.writing_center_controller import WritingCenterController as wcc

View.register(app)
MessageCenterView.register(app)
AppointmentsView.register(app)
CronView.register(app)
ProfileView.register(app)
SchedulesView.register(app)
SettingsView.register(app)
StatisticsView.register(app)
UsersView.register(app)


# This makes these variables open to use everywhere
@app.context_processor
def utility_processor():
    to_return = {}
    to_return.update({
        'now': datetime.now(),
        'alert': wcc().get_alert(),
    })

    return to_return


def datetimeformat(value, custom_format=None):
    if value:
        if custom_format:
            return value.strftime(custom_format)

        if value.strftime('%l:%M:%p') == '12:00AM':  # Check for midnight
            return 'midnight'

        if value.strftime('%l:%M:%p') == '12:00PM':  # Check for noon
            return 'noon'

        if value.strftime('%M') == '00':
            time = value.strftime('%l')
        else:
            time = value.strftime('%l:%M')

        if value.strftime('%p') == 'PM':
            time = '{0} {1}'.format(time, 'p.m.')
        else:
            time = '{0} {1}'.format(time, 'a.m.')

        return time

    else:
        return '???'


app.jinja_env.filters['datetimeformat'] = datetimeformat


@app.before_request
def before_request():
    if '/static/' in request.path \
            or '/assets/' in request.path \
            or '/cron/' in request.path \
            or '/no-cas/' in request.path:

        if 'ALERT' not in flask_session.keys():
            flask_session['ALERT'] = []
    else:
        if 'USERNAME' not in flask_session.keys():
            if app.config['ENVIRON'] == 'prod':
                username = request.environ.get('REMOTE_USER')
            else:
                username = app.config['TEST_USERNAME']
            current_user = uc().get_user_by_username(username)
            if not current_user:
                # current_user = User().create_user_at_sign_in(username)
                pass
            # if current_user.deletedAt != None:  # User has been soft deleted in the past, needs reactivating
            #     User().activate_existing_user(current_user.username)
            flask_session['USERNAME'] = current_user.username
            flask_session['NAME'] = '{0} {1}'.format(current_user.firstName, current_user.lastName)
            flask_session['USER-ROLES'] = []
            user_roles = uc().get_user_roles(current_user.id)
            for role in user_roles:
                flask_session['USER-ROLES'].append(role.name)
        if 'NAME' not in flask_session.keys():
            flask_session['NAME'] = flask_session['USERNAME']
        if 'USER-ROLES' not in flask_session.keys():
            flask_session['USER-ROLES'] = ['STUDENT']
        if 'ADMIN-VIEWER' not in flask_session.keys():
            flask_session['ADMIN-VIEWER'] = False
        if 'ALERT' not in flask_session.keys():
            flask_session['ALERT'] = []
        if 'DATE-SELECTOR-START' not in flask_session.keys() and 'DATE-SELECTOR-END' not in flask_session.keys() \
                and 'DATE-SELECTOR-VALUE' not in flask_session.keys():
            start = datetime.now()
            start = start.replace(hour=0, minute=0, second=0)
            end = datetime.now()
            end = end.replace(hour=23, minute=59, second=59)
            flask_session['DATE-SELECTOR-START'] = start
            flask_session['DATE-SELECTOR-END'] = end
            flask_session['DATE-SELECTOR-VALUE'] = 'all'


@app.after_request
def close_db_session(response):
    # This closes the db session to allow the data to propogate to all threads. It's available for use again right away.
    db_session.close()
    return response
