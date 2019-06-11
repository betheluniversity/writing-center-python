import logging

from flask import Flask, request
from flask import session as flask_session
from datetime import datetime
from raven.contrib.flask import Sentry

app = Flask(__name__)
app.config.from_object('config')

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


@app.before_request
def before_request():
    if '/static/' in request.path \
            or '/assets/' in request.path \
            or '/cron/' in request.path \
            or '/no-cas/' in request.path:

        if 'ALERT' not in flask_session.keys():
            flask_session['ALERT'] = []
    else:
        if 'ALERT' not in flask_session.keys():
            flask_session['ALERT'] = []



    flask_session['NAME'] = app.config["TEST_NAME"]
