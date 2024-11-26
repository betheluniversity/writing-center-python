# Packages
import socket
from flask import render_template, session as flask_session
from flask_mail import Mail, Message
from datetime import datetime

# Local
from writing_center import app
from writing_center.db_repository import db_session
from writing_center.db_repository.tables import UserTable, EmailPreferencesTable, AppointmentsTable, UserRoleTable, \
    RoleTable, SettingsTable


class MessageCenterController:

    def __init__(self):
        pass

    def toggle_substitute(self, substitute):
        toggle = self.get_email_preferences()
        toggle.subRequestEmail = substitute
        db_session.commit()
        return 'success'

    def toggle_shift(self, shift):
        toggle = self.get_email_preferences()
        toggle.studentSignUpEmail = shift
        db_session.commit()
        return 'success'

    def get_active_users(self):
        return (db_session.query(UserTable)
                .filter(UserTable.deletedAt == None)
                .all())

    def get_roles(self):
        return (db_session.query(RoleTable)
                .all())

    def get_email_preferences(self):
        user = self.get_user(flask_session['USERNAME'])
        return (db_session.query(EmailPreferencesTable)
                .filter(EmailPreferencesTable.user_id == user.id)
                .one())

    def get_email_preferences_by_id(self, user_id):
        return (db_session.query(EmailPreferencesTable)
                .filter(EmailPreferencesTable.user_id == user_id)
                .one())

    def get_appointment_info(self, appointment_id):
        return (db_session.query(AppointmentsTable)
                .filter(AppointmentsTable.id == appointment_id)
                .one())

    def get_user(self, username):
        return (db_session.query(UserTable)
                .filter(UserTable.username == username)
                .one())

    def get_user_by_id(self, id):
        return (db_session.query(UserTable)
                .filter(UserTable.id == id)
                .one_or_none())

    def get_user_roles(self, user_id):
        return (db_session.query(UserRoleTable)
                .filter(UserRoleTable.user_id == user_id)
                .one())

    def get_substitute_email_recipients(self):
        users = db_session.query(UserTable)\
            .join(EmailPreferencesTable, UserTable.id == EmailPreferencesTable.user_id)\
            .join(UserRoleTable, UserTable.id == UserRoleTable.user_id)\
            .join(RoleTable, UserRoleTable.role_id == RoleTable.id)\
            .filter(EmailPreferencesTable.subRequestEmail == 1)\
            .filter((RoleTable.name == 'Tutor') | (RoleTable.name == 'Administrator'))\
            .filter(UserTable.deletedAt == None)\
            .all()

        recipients = []
        for user in users:
            recipients.append(user.email)

        current_user = self.get_user(flask_session['USERNAME'])
        if current_user.email not in recipients:
            recipients.append(current_user.email)

        return recipients

    def close_session_student(self, appointment_id):
        appointment = self.get_appointment_info(appointment_id)
        student = self.get_user_by_id(appointment.student_id)
        tutor = self.get_user_by_id(appointment.tutor_id)

        if appointment.scheduledStart and appointment.scheduledEnd:
            appt_info = {'tutor': tutor.firstName + " " + tutor.lastName,
                         'date': appointment.scheduledStart.date().strftime("%m/%d/%Y"),
                         'time': appointment.scheduledStart.time().strftime("%I:%M %p") + " - " + appointment.scheduledEnd.time().strftime("%I:%M %p"),
                         'assignment': appointment.assignment,
                         'notes': appointment.notes,
                         'suggestions': appointment.suggestions}
        elif appointment.actualStart and appointment.actualEnd:
            appt_info = {'tutor': tutor.firstName + " " + tutor.lastName,
                         'date': appointment.actualStart.date().strftime("%m/%d/%Y"),
                         'time': appointment.actualStart.time().strftime("%I:%M %p") + " - " + appointment.actualEnd.time().strftime("%I:%M %p"),
                         'assignment': appointment.assignment,
                         'notes': appointment.notes,
                         'suggestions': appointment.suggestions}

        subject = 'Appointment with {0} {1}'.format(tutor.firstName, tutor.lastName)

        recipients = student.email

        self.send_message(subject, render_template('emails/session_email_student.html', **locals()), recipients, bcc='', html=True)

    def appointment_signup_student(self, appointment_id):
        # get the appointment via the appointment id
        appointment = self.get_appointment_info(appointment_id)
        virtual = appointment.online
        student = self.get_user_by_id(appointment.student_id)
        tutor = self.get_user_by_id(appointment.tutor_id)
        appt_info = {'date': appointment.scheduledStart.date().strftime("%m/%d/%Y"),
                     'time': appointment.scheduledStart.time().strftime("%I:%M %p"),
                     'tutor': tutor.firstName + ' ' + tutor.lastName}
        # other email information: recipient, subject, body
        if virtual == 0:
            subject = 'F2F Writing Center Appointment {0}'.format(appointment.scheduledStart.date())
        else:
            subject = 'Virtual Writing Center Appointment {0}'.format(appointment.scheduledStart.date())

        recipient = student.email
        qualtrics_link = self.get_survey_link()[0]
        zoom_url = self.get_zoom_url()[0]

        if self.send_message(subject, render_template('emails/appointment_signup_student.html', **locals()), recipient, bcc='', html=True):
            return True
        return False

    def get_survey_link(self):
        return db_session.query(SettingsTable.value)\
            .filter(SettingsTable.id == 4)\
            .one_or_none()

    def get_zoom_url(self):
        return db_session.query(SettingsTable.value) \
            .filter(SettingsTable.id == 5) \
            .one_or_none()

    def appointment_signup_tutor(self, appointment_id):
        appointment = self.get_appointment_info(appointment_id)
        student = self.get_user_by_id(appointment.student_id)
        tutor = self.get_user_by_id(appointment.tutor_id)
        if self.get_email_preferences_by_id(tutor.id).studentSignUpEmail == 1:
            appt_info = {'date': appointment.scheduledStart.date().strftime("%m/%d/%Y"),
                         'time': appointment.scheduledStart.time().strftime("%I:%M %p"),
                         'student': student.firstName + ' ' + student.lastName,
                         'student-email': student.email,
                         'assignment': appointment.assignment}

            # other email information: recipient, body, subject
            subject = 'Appointment Scheduled'

            recipient = tutor.email

            if self.send_message(subject, render_template('emails/appointment_signup_tutor.html', **locals()), recipient, bcc='', html=True):
                return True
            return False
        return False

    def request_substitute(self, appointment_id):
        appointment = self.get_appointment_info(appointment_id)
        student = self.get_user_by_id(appointment.student_id)
        tutor = self.get_user_by_id(appointment.tutor_id)

        appt_info = {'date': appointment.scheduledStart.date().strftime("%m/%d/%Y"),
                     'time': appointment.scheduledStart.time().strftime("%I:%M %p"),
                     'student': '{0} {1}'.format(student.firstName, student.lastName) if student else 'None',
                     'assignment': appointment.assignment,
                     'tutor': tutor.firstName + ' ' + tutor.lastName}

        subject = '{0} is requesting a substitute on {1}'.format(appt_info['tutor'], appt_info['date'])

        recipients = self.get_substitute_email_recipients()

        if self.send_message(subject, render_template('emails/sub_request.html', **locals()), recipients, bcc='', html=True):
            return True
        return False

    def substitute_request_filled(self, appointment_id):
        appointment = self.get_appointment_info(appointment_id)
        old_tutor = self.get_user_by_id(appointment.tutor_id)
        sub_tutor = self.get_user(flask_session['USERNAME'])

        subject = 'Substitute Request Filled'

        recipient = old_tutor.email

        if self.send_message(subject, render_template('emails/sub_request_fulfilled.html', **locals()), recipient, bcc='', html=True):
            return True
        return False

    def cancel_appointment_student(self, appointment_id):
        appointment = self.get_appointment_info(appointment_id)
        tutor = self.get_user_by_id(appointment.tutor_id)

        appt_info = {
            'date': appointment.scheduledStart.date().strftime("%m/%d/%Y"),
            'time': appointment.scheduledStart.time().strftime("%I:%M %p"),
            'tutor': '{0} {1}'.format(tutor.firstName, tutor.lastName)
        }

        subject = 'Appointment Cancelled'

        recipient = tutor.email

        if self.send_message(subject, render_template('emails/cancel_appointment.html', **locals()), recipient, bcc='', html=True):
            return True
        return False

    def end_appt_prof(self, appt_id):
        appointment = self.get_appointment_info(appt_id)
        if appointment.profEmail:
            tutor = self.get_user_by_id(appointment.tutor_id)
            student = self.get_user_by_id(appointment.student_id)

            appt_info = {
                'date': appointment.actualStart.date().strftime("%m/%d/%Y"),
                'time': '{0} - {1}'.format(appointment.actualStart.time().strftime("%I:%M %p"),
                                           appointment.actualEnd.time().strftime("%I:%M %p")),
                'tutor': '{0} {1}'.format(tutor.firstName, tutor.lastName),
                'student': '{0} {1}'.format(student.firstName, student.lastName),
                'assignment': appointment.assignment,
                'notes': appointment.notes,
                'suggestions': appointment.suggestions,
                'course': '{0} Section {1}'.format(appointment.courseCode, appointment.courseSection)
            }

            subject = '{0} {1} Writing Center Appointment'.format(student.firstName, student.lastName)

            recipient = appointment.profEmail

            if self.send_message(subject, render_template('emails/prof_email.html', **locals()), recipient, bcc='', html=True):
                return True
        return False

    def get_cc(self, cc_ids):
        emails = []
        for cc in cc_ids:
            emails.append(self.get_user_email(int(cc)))
        return emails

    def get_bcc(self, groups, bcc_ids):
        emails = []
        for bcc in bcc_ids:
            emails.append(self.get_user_email(int(bcc)))

        for group in groups:
            group_users = self.get_group_active_users(int(group))
            for user in group_users:
                emails.append(user.email)

        return emails

    def get_user_email(self, user_id):
        user = db_session.query(UserTable).filter(UserTable.id == user_id).one()
        return user.email

    def get_group_active_users(self, role_id):
        return db_session.query(UserTable).filter(UserTable.id == UserRoleTable.user_id)\
            .filter(UserRoleTable.role_id == role_id).filter(UserTable.deletedAt == None).all()

    def send_message(self, subject, body, recipients, bcc, html=False):
        # data will be compiled in the above functions and sent here
        if app.config['ENVIRON'] != 'prod':
            print('Would have sent email to: {0}, bcc: {1}'.format(str(recipients), str(bcc)))
            subject = '{0}: Would have sent email to - {1}, bcc: {2}'.format(subject, str(recipients), str(bcc))
            recipients = app.config['TEST_EMAIL']
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
