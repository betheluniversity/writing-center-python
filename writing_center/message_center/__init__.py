# Packages
from flask import render_template, request, redirect, url_for
from flask_classy import FlaskView, route

# Local
from writing_center.message_center.message_center_controller import MessageCenterController


class MessageCenterView(FlaskView):
    route_base = 'message-center'

    def __init__(self):
        self.base = MessageCenterController()

    @route('/')
    def index(self):
        users = self.base.get_all_users()
        users = sorted(users, key=lambda i: i.lastName)
        roles = self.base.get_roles()
        roles = sorted(roles, key=lambda i: i.id)
        return render_template('message_center/send-email.html', **locals())
    
    @route('/send', methods=['POST'])
    def send(self):
        data = request.form  # The recipient is changing to croups, so some logic to get the right recipients is nececssary
        # grab the group(s) from the form, use the group id to get the emails of all the people in the group(s)
        groups = data['recipients']
        # recipients = self.base.get_group_emails(groups)
        # need to check that all the stuff is actually filled in, if its not, we need to fill it with an empty value
        return self.base.send_message(data['subject'], data['message'], data['recipients'], data['cc'], data['bcc'])

    @route('/close-student', methods=['POST'])
    def close_session_student(self):
        data = request.form
        return self.base.close_session_student(data['appointment_id'])

    @route('/close-tutor', methods=['POST'])
    def close_session_tutor(self):
        data = request.form
        return self.base.close_session_tutor(data['appointment_id'], data['to_prof'])
