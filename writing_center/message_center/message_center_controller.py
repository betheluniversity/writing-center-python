# Packages
import socket
from flask import render_template, session
from flask_mail import Mail, Message

# Local
from writing_center import app
from writing_center.db_repository.message_center_functions import Message_Center


class MessageCenterController:

    def __init__(self):
        self.message_center = Message_Center()

    def manage_message_preferences(self, substitute, shift):
        self.message_center.change_email_preferences(substitute, shift, session['user_id'])
        return render_template('message_center/preferences.html', **locals())

    def get_message_preferences(self):
        return self.message_center.get_email_preferences(session['user_id'])

    def close_session_email(self, appointment_id):  # TODO: refactor to work with appointments
        appointment = self.message_center.get_appointment_info(appointment_id)
        subject = '{{{0}}} {1} ({2})'.format(app.config['LAB_TITLE'], appointment.StudentUsername, appointment.date.strftime('%m/%d/%Y'))
        tutor = appointment.TutorUsername
        recipients = self.user.get_end_of_session_recipients()  # Not sure what to put here
        session_courses = self.course.get_courses_for_session(session_id)  # Not sure what toput here

        for recipient in recipients:
            recipient_roles = self.user.get_user_roles(recipient.id)  # will use the same people as recipient
            recipient_role_names = []

            for role in recipient_roles:
                recipient_role_names.append(role.name)
            students_and_courses = {}
            courses_and_info = {}

            if 'Administrator' in recipient_role_names:
                session_students = self.session.get_session_students(session_id)
                for student in session_students:
                    students_and_courses[student] = self.session.get_report_student_session_courses(session_id, student.id)  # Gets courses attended

                for course in session_courses:
                    courses_and_info[course] = {}
                    courses_and_info[course]['students'] = self.session.get_session_course_students(session_id, course.id)  # Gets students for a course in a specific session
                    courses_and_info[course]['profs'] = self.course.get_profs_from_course(course.id)

            else:  # They must be a prof since get_end_of_session_recipients only gets admins and profs
                professor_courses = self.course.get_professor_courses(recipient.id, sess.semester_id)
                professor_course_ids = []
                for course in professor_courses:
                    professor_course_ids.append(course.id)

                for course in session_courses:
                    if course.id in professor_course_ids:
                        courses_and_info[course] = {}
                        courses_and_info[course]['students'] = self.session.get_session_course_students(session_id,
                                                                                                        course.id)  # Same as above
                        courses_and_info[course]['profs'] = self.course.get_profs_from_course(course.id)

                session_students = self.session.get_prof_session_students(session_id,
                                                                          professor_course_ids)  # Gets students specific to prof
                for student in session_students:
                    students_and_courses[student] = self.session.get_report_student_session_courses(session_id,
                                                                                                    student.id)  # Same as above

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
