# Packages
import socket
from flask import render_template, session
from flask_mail import Mail, Message

# Local
from writing_center import app
from writing_center.db_repository.message_center_functions import MessageCenter
from writing_center.db_repository.user_functions import UserFunctions


class MessageCenterController:

    def __init__(self):
        self.message_center = MessageCenter()
        self.user = UserFunctions()

    def toggle_substitute(self, substitute):
        self.message_center.change_email_preferences(substitute, self.message_center.get_email_preferences(self.user.get_user(session['USERNAME']).id).shift, self.user.get_user(session['USERNAME']).id)
        return

    def toggle_shift(self, shift):
        print('made it to toggle shift')
        return

    def get_message_preferences(self):
        return self.message_center.get_email_preferences(self.user.get_user(session['USERNAME']).id)

    def close_session_email(self, appointment_id):  # TODO: refactor to work with appointments
        appointment = self.message_center.get_appointment_info(appointment_id)
        student = self.user.get_user(appointment.StudUsername)

        if appointment.ProfUsername != '':
            professor = self.user.get_user(appointment.ProfUsername)

        tutor = self.user.get_user(appointment.TutorUsername)
        subject = '{{{0}}} {1} ({2})'.format(appointment.StudUsername, appointment.StudentUsername, appointment.date.strftime('%m/%d/%Y'))
        tutor = appointment.TutorUsername
        recipients = self.user.get_end_of_session_recipients(appointment_id)

        for recipient in recipients:
            recipient_roles = self.user.get_user_roles(recipient.id)
            recipient_role_names = []

            for role in recipient_roles:
                recipient_role_names.append(role.name)

            self.send_message(subject, render_template('sessions/email.html', **locals()), recipient.email, None, True)

    def send_message(self, subject, body, recipients, bcc, html=False):
        if app.config['ENVIRON'] != 'prod':
            print('Would have sent email to: {0} {1}'.format(str(recipients), str(bcc)))
            subject = '{0} {1} {2}'.format(subject, str(recipients), str(bcc))
            recipients = app.config['TEST_EMAILS']
            bcc = []

        # if we are sending a message to a single user, go ahead and convert the string into a list
        if isinstance(recipients, str):
            recipients = [recipients]
        if isinstance(bcc, str):
            bcc = [bcc]

        mail = Mail(app)
        msg = Message(subject=subject,
                      sender='noreply@bethel.edu',
                      recipients=recipients,
                      bcc=bcc)
        if html:
            msg.html = body
        else:
            msg.body = body
        try:
            mail.send(msg)
        except socket.error:
            print("Failed to send message: {}".format(body))
            return False
        return True
