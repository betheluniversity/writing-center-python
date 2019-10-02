from flask import Response, request, render_template
from flask_classy import FlaskView, route
from functools import wraps

from writing_center import app
from writing_center.message_center.message_center_controller import MessageCenterController
from writing_center.cron.cron_controller import CronController


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == app.config['WC_LOGIN']['username'] and password == app.config['WC_LOGIN']['password']


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)

    return decorated


class CronView(FlaskView):
    route_base = 'cron'

    def __init__(self):
        self.mail = MessageCenterController()
        self.cron = CronController()

    @requires_auth
    @route('/reminders', methods=['get'])
    def send_reminder_emails(self):
        cron_message = "Cron sending reminder emails...\n"
        try:
            upcoming_appointments = self.cron.get_upcoming_appointments()
            for appointment in upcoming_appointments:
                tutor = self.cron.get_user(appointment.tutor_id)
                student = self.cron.get_user(appointment.student_id)
                subject = "Your Upcoming Appointment"
                appt_info = {'date': appointment.scheduledStart.date().strftime("%m/%d/%Y"),
                             'time': appointment.scheduledStart.time().strftime("%I:%M %p"),
                             'tutor': tutor.firstName + ' ' + tutor.lastName}
                if appointment.multilingual:
                    if self.mail.send_message(subject, render_template('emails/upcoming_email_multilingual.html', **locals()), student.email, cc='', bcc='', html=True):
                        cron_message += "Email sent successfully to {0} {1}\n".format(student.firstName, student.lastName)
                else:
                    if self.mail.send_message(subject, render_template('emails/upcoming_email.html', **locals()), student.email, cc='', bcc='', html=True):
                        cron_message += "Email sent successfully to {0} {1}\n".format(student.firstName, student.lastName)
            cron_message += "All reminders sent\n\n"
            return cron_message
        except Exception as error:
            cron_message += "An error occurred: {0}\n\n".format(str(error))
            return cron_message
