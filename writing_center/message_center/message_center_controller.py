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

    def manage_message_preferences(self, substitute, shift):
        self.message_center.change_email_preferences(substitute, shift, session['user_id'])
        return render_template('message_center/preferences.html', **locals())

    def get_message_preferences(self):
        return self.message_center.get_email_preferences(session['user_id'])

    def close_session_email(self, appointment_id):  # TODO: refactor to work with appointments
        appointment = self.message_center.get_appointment_info(appointment_id)
        student = self.user.get_user(appointment['StudUsername'])
        professor = self.user.get_user(appointment['ProfUsername'])
        subject = '{{{0}}} {1} ({2})'.format(app.config['LAB_TITLE'], appointment.StudentUsername, appointment.date.strftime('%m/%d/%Y'))
        tutor = appointment.TutorUsername
        recipients = self.user.get_end_of_session_recipients()  # Not sure what to put here

        for recipient in recipients:
            recipient_roles = self.user.get_user_roles(recipient.id)  # will use the same people as recipient
            recipient_role_names = []

            for role in recipient_roles:
                recipient_role_names.append(role.name)

            email_info = []

            if 'Administrator' in recipient_role_names:
                email_info.append({'student_name': student['FirstName'] + ' ' + student['LastName'],
                                   'professor_name': professor['FirstName'] + ' ' + professor['LastName'],
                                   'notes': appointment['Notes'],
                                   'suggestion': appointment['Suggestions'],
                                   'course': appointment['CourseCode'],
                                   'assignment': appointment['Assignment']})

            else:  # They must be a prof since get_end_of_session_recipients only gets admins and profs
                email_info.append({'student_name': student['FirstName'] + ' ' + student['LastName'],
                                   'notes': appointment['Notes'],
                                   'suggestion': appointment['Suggestions'],
                                   'course': appointment['CourseCode'],
                                   'assignment': appointment['Assignment']})

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
