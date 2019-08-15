# Packages
from flask import render_template, request, redirect, url_for
from flask_classy import FlaskView, route

# Local
from writing_center.message_center.message_center_controller import MessageCenterController
from writing_center.writing_center_controller import WritingCenterController


class MessageCenterView(FlaskView):
    route_base = 'message-center'

    def __init__(self):
        self.base = MessageCenterController()
        self.wcc = WritingCenterController()

    @route('/')
    def index(self):
        self.wcc.check_roles_and_route(['Administrator'])
        users = self.base.get_active_users()
        users = sorted(users, key=lambda i: i.lastName)
        roles = self.base.get_roles()
        roles = sorted(roles, key=lambda i: i.id)
        return render_template('message_center/send-email.html', **locals())
    
    @route('/send', methods=['POST'])
    def send(self):
        self.wcc.check_roles_and_route(['Administrator'])
        data = request.form
        # grab the group(s) from the form, use the group id to get the emails of all the people in the group(s)
        groups = data['recipients']
        # need to check that all the stuff is actually filled in, if its not, we need to fill it with an empty value
        return self.base.send_message(data['subject'], data['message'], data['recipients'], data['cc'], data['bcc'])

    @route('/close-student', methods=['POST'])
    def close_session_student(self):  # this needs to be connected to the appointment end page
        # TODO ADD CORRECT ROLES TO ROUTE CHECK BELOW
        # self.wcc.check_roles_and_route(['Administrator'])
        data = request.form
        return self.base.close_session_student(data['appointment_id'])

    @route('/close-tutor', methods=['POST'])
    def close_session_tutor(self):  # this needs to be connected to the appointment end page
        # TODO ADD CORRECT ROLES TO ROUTE CHECK BELOW
        # self.wcc.check_roles_and_route(['Administrator'])
        data = request.form
        return self.base.close_session_tutor(data['appointment_id'], data['to_prof'])
