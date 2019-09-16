# Packages
from flask import render_template, request, redirect, url_for
from flask_classy import FlaskView, route

# Local
from writing_center.message_center.message_center_controller import MessageCenterController
from writing_center.writing_center_controller import WritingCenterController


class MessageCenterView(FlaskView):
    route_base = 'message-center'

    def __init__(self):
        self.mcc = MessageCenterController()
        self.wcc = WritingCenterController()

    @route('/')
    def index(self):
        self.wcc.check_roles_and_route(['Administrator'])
        users = self.mcc.get_active_users()
        users = sorted(users, key=lambda i: i.lastName)
        roles = self.mcc.get_roles()
        roles = sorted(roles, key=lambda i: i.id)
        return render_template('message_center/send-email.html', **locals())
    
    @route('/send', methods=['POST'])
    def send(self):
        immutable_data = request.form
        data = immutable_data.copy()
        # make sure there are no duplicates in the email list
        subject = data.get('subject')
        message = data.get('message')
        recipients = data.get('recipients')
        cc = data.get('cc')
        bcc = data.get('bcc')
        if self.base.send_message(subject, message, recipients, cc, bcc):
            self.wcc.set_alert('success', 'Email sent successfully!')
        else:
            self.wcc.set_alert('danger', 'Email failed to send.')
        return redirect(url_for('MessageCenterView:index'))

    @route('/close-student', methods=['POST'])
    def close_session_student(self):  # this needs to be connected to the appointment end page
        # TODO ADD CORRECT ROLES TO ROUTE CHECK BELOW
        # self.wcc.check_roles_and_route(['Administrator'])
        data = request.form
        return self.mcc.close_session_student(data['appointment_id'])

    @route('/close-tutor', methods=['POST'])
    def close_session_tutor(self):  # this needs to be connected to the appointment end page
        # TODO ADD CORRECT ROLES TO ROUTE CHECK BELOW
        # self.wcc.check_roles_and_route(['Administrator'])
        data = request.form
        return self.mcc.close_session_tutor(data['appointment_id'], data['to_prof'])
