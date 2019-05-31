import logging

from flask import Flask
from flask import session as flask_session
from datetime import datetime
from raven.contrib.flask import Sentry

app = Flask(__name__)
app.config.from_object('config')
app.debug = True

# sentry = Sentry(app, dsn=app.config['SENTRY_URL'], logging=True, level=logging.INFO)
# if app.config['ENVIRON'] == 'prod':
#     from writing_center import error

# Declaring and registering the views
from writing_center.views import View
from writing_center.appointments import AppointmentsView
from writing_center.cron import CronView
from writing_center.email_tab import EmailView
from writing_center.profile import ProfileView
from writing_center.schedules import SchedulesView
from writing_center.settings import SettingsView
from writing_center.statistics import StatisticsView
from writing_center.users import UsersView
View.register(app)
AppointmentsView.register(app)
CronView.register(app)
EmailView.register(app)
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


if __name__ == "__main__":
    app.run()
