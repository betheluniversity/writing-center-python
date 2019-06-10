import logging

from flask import Flask
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
    })

    return to_return


@app.before_request
def before_request():
    flask_session['NAME'] = app.config["TEST_NAME"]


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
