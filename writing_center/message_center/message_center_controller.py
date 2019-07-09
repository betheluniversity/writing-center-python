# Packages
import socket
from flask import render_template, session
from flask_classy import route
from flask_mail import Mail, Message

# Local
from writing_center import app
from writing_center.db_repository import db_session
from writing_center.db_repository.tables import UserTable, EmailPreferencesTable, AppointmentsTable, UserRoleTable, RoleTable


class MessageCenterController:

    def __init__(self):
        pass

    def get_all_users(self):
        return (db_session.query(UserTable)
                .all())

    def get_email_preferences(self):
        user = self.get_user(session['USERNAME'])
        return (db_session.query(EmailPreferencesTable)
                .filter(EmailPreferencesTable.user_id == user.id)
                .one())

    def get_appointment_info(self, appointment_id):
        return (db_session.query(AppointmentsTable)
                .filter(AppointmentsTable.ID == appointment_id)
                .one())

    def get_user(self, username):
        return (db_session.query(UserTable)
                .filter(UserTable.username == username)
                .one())

    def get_user_by_id(self, id):
        return (db_session.query(UserTable)
                .filter(UserTable.id == id)
                .one())

    def get_user_roles(self, user_id):
        return (db_session.query(UserRoleTable)
                .filter(UserRoleTable.user_id == user_id)
                .one())

    def get_end_of_session_recipients(self, appointment_id):
        appointment = (db_session.query(AppointmentsTable)
                       .filter(AppointmentsTable.ID == appointment_id)
                       .all())

        recipients = [appointment.profEmail, self.get_user(appointment.student_id).email]
        return recipients

    def get_substitute_email_recipients(self):
        users = (db_session.query(EmailPreferencesTable.user_id)
                 .filter(EmailPreferencesTable.SubRequestEmail == 1)
                 .all())

        users.append(db_session.query(UserRoleTable.user_id)
                     .filter(UserRoleTable.role_id == 1 or UserRoleTable.role_id == 2)
                     .all())

        users = list(dict.fromkeys(users))
        recipients = []
        for user in users:
            recipients.append(self.get_user_by_id(user).email)

        return recipients

    def get_shift_email_recipients(self, appointment_id):
        users = []

        users.append(self.get_appointment_info(appointment_id).tutor_id)

        users.append(db_session.query(UserRoleTable.user_id)
                     .filter(UserRoleTable.role_id == 1 or UserRoleTable.role_id == 2)
                     .all())

        users = list(dict.fromkeys(users))
        recipients = []
        for user in users:
            recipients.append(self.get_user_by_id(user).email)

        return recipients

    def toggle_substitute(self, substitute):
        user = (db_session.query(UserTable)
                .filter(UserTable.username == session['USERNAME'])
                .one())
        toggle = self.get_email_preferences()
        toggle.SubRequestEmail = substitute
        db_session.commit()
        return 'success'

    def toggle_shift(self, shift):
        user = (db_session.query(UserTable)
                .filter(UserTable.username == session['USERNAME'])
                .one())
        toggle = self.get_email_preferences()
        toggle.StudentSignUpEmail = shift
        db_session.commit()
        return 'success'

    def close_session_email(self, appointment_id):
        appointment = self.get_appointment_info(appointment_id)
        student = self.get_user(appointment.StudUsername)

        if appointment.ProfUsername != '':
            professor = self.get_user(appointment.ProfUsername)

        tutor = self.get_user(appointment.TutorUsername)
        subject = '{{{0}}} {1} ({2})'.format(appointment.StudUsername, appointment.StudentUsername,
                                             appointment.date.strftime('%m/%d/%Y'))  # TODO work this out
        tutor = appointment.TutorUsername
        recipients = self.get_end_of_session_recipients(appointment_id)

        self.send_message(subject, render_template('sessions/email.html', **locals()), recipients, None, True)

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

    def send_shift_message(self):
        # TODO write the function to send an email when a student signs up for a shift
        pass

    @route('/sub-email')
    def send_substitute_email(self, appointment_id):
        recipients = self.get_substitute_email_recipients()
        appointment = self.get_appointment_info(appointment_id)
        email_info = {'student': self.get_user_by_id(appointment.student_id).firstName + ' ' + self.get_user_by_id(
            appointment.student_id).lastName,
                      'tutor': self.get_user_by_id(appointment.tutor_id).firstName + ' ' + self.get_user_by_id(
                          appointment.tutor_id).lastName,
                      'start': appointment.scheduledStart, 'end': appointment.scheduledEnd,
                      'assignment': appointment.assignment, 'date': 'NEED THIS'}

        mail = Mail(app)
        msg = Message(subject='Substitute Tutor needed',
                      sender='',
                      recipients=recipients)

        msg.html = 'sub_request_body.html'

        if app.config['ENVIRON'] != 'prod':
            print('Would have sent email to: {}'.format(str(recipients)))
            print('Subject: {}'.format(msg.subject))
            print('Body: {}'.format(msg.html))
            return True
        else:
            try:
                mail.send(msg)
            except socket.error:
                print("Failed to send message: {}".format(msg.html))
                return False
            return True
