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
        user = self.get_user(session['USERNAME'])
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
                .one())

    def get_user_roles(self, user_id):
        return (db_session.query(UserRoleTable)
                .filter(UserRoleTable.user_id == user_id)
                .one())

    def get_substitute_email_recipients(self):
        # TODO: Logic to ensure we dont send this email to the tutor requesting a sub
        # Should just be matching the user id to the session user id
        users = (db_session.query(EmailPreferencesTable.user_id)
                 .filter(EmailPreferencesTable.SubRequestEmail == 1)
                 .all())

        users.append(db_session.query(UserRoleTable.user_id)
                     .filter(UserRoleTable.role_id == 1 or UserRoleTable.role_id == 2)
                     .all())

        users = list(dict.fromkeys(users))
        recipients = []
        for user in users:
            if user.username != session['USERNAME']:
                recipients.append(self.get_user_by_id(user).email)

        return recipients

    def close_session_student(self, appointment_id):  # todo needs to be connected
        appointment = self.get_appointment_info(appointment_id)
        student = self.get_user_by_id(appointment.student_id)
        tutor = self.get_user_by_id(appointment.tutor_id)

        appt_info = {'tutor': tutor.firstName + tutor.lastName,
                     'actual_start': appointment.actualStart,
                     'actual_end': appointment.actualEnd,
                     'assignment': appointment.assignment,
                     'notes': appointment.notes,
                     'suggestions': appointment.suggestions}

        subject = 'Appointment with {0} {1}'.format(tutor.firstName, tutor.lastName)

        recipients = student.email

        self.send_message(subject, render_template('emails/session_email_student.html', **locals()), recipients, cc='', bcc='')

    def close_session_tutor(self, appointment_id, to_prof):  # Todo needs to be connected
        appointment = self.get_appointment_info(appointment_id)
        student = self.get_user_by_id(appointment.student_id)

        if appointment.ProfUsername != '':
            professor = appointment.profName
        else:
            professor = 'n/a'

        if appointment.dropIn == 0:
            appt_type = 'Scheduled'
        else:
            appt_type = 'Drop In'

        tutor = self.get_user_by_id(appointment.tutor_id)

        appt_info = {'student': student.FirstName + student.LastName,
                     'type': appt_type,
                     'actual_start': appointment.actualStart,
                     'actual_end': appointment.actualEnd,
                     'assignment': appointment.assignment}

        subject = 'Appointment with {0} {1}'.format(student.firstName, student.lastName)

        recipients = tutor.email

        if to_prof:
            cc = appointment.profEmail
            self.send_message(subject, render_template('emails/session_email_tutor.html', **locals()), recipients, cc, bcc='')
        else:
            self.send_message(subject, render_template('emails/session_email_tutor.html', **locals()), recipients, cc='', bcc='')

    def appointment_signup_student(self, appointment_id):
        # get the appointment via the appointment id
        appointment = self.get_appointment_info(appointment_id)
        student = self.get_user_by_id(appointment.student_id)
        tutor = self.get_user_by_id(appointment.tutor_id)
        appt_info = {'date': appointment.scheduledStart.date(),
                     'time': appointment.scheduledStart.time(),
                     'tutor': tutor.firstName + ' ' + tutor.lastName}
        # other email information: recipient, subject, body
        subject = 'Appointment on {0}'.format(appointment.scheduledStart.date())

        recipient = student.email

        if self.send_message(subject, render_template('emails/appointment_signup_student.html', **locals()), recipient, cc='', bcc=''):
            return True
        else:
            return False

    def appointment_signup_tutor(self, appointment_id):
            appointment = self.get_appointment_info(appointment_id)
            student = self.get_user_by_id(appointment.student_id)
            tutor = self.get_user_by_id(appointment.tutor_id)
            if self.get_email_preferences_by_id(tutor.id).studentSignUpEmail == 1:
                appt_info = {'date': appointment.scheduledStart.date(),
                             'time': appointment.scheduledStart.time(),
                             'student': student.firstName + ' ' + student.lastName,
                             'assignment': appointment.assignment}

                # other email information: recipient, body, subject
                subject = 'Appointment Scheduled'

                recipient = tutor.email

                if self.send_message(subject, render_template('emails/appointment_signup_tutor.html', **locals()), recipient, cc='', bcc=''):
                    return True
                else:
                    return False
            else:
                return False

    def send_message(self, subject, body, recipients, cc, bcc, html=False):
        # data will be compiled in the above functions and sent here
        if app.config['ENVIRON'] != 'prod':
            print('Would have sent email to: {0} cc: {1}, bcc: {2}'.format(str(recipients), str(cc), str(bcc)))
            subject = '{0}'.format(subject)

        # if we are sending a message to a single user, go ahead and convert the string into a list
        if isinstance(recipients, str):
            recipients = [recipients]
        if isinstance(bcc, str):
            bcc = [bcc]
        if isinstance(cc, str):
            cc = [cc]

        mail = Mail(app)
        msg = Message(subject=subject,
                      sender='noreply@bethel.edu',
                      recipients=recipients,
                      cc=cc,
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
