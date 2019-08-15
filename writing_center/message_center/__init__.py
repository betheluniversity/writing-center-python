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
        users = self.base.get_active_users()
        users = sorted(users, key=lambda i: i.lastName)
        roles = self.base.get_roles()
        roles = sorted(roles, key=lambda i: i.id)
        return render_template('message_center/send-email.html', **locals())
    
    @route('/send', methods=['POST'])
    def send(self):
        data = request.form
        # grab the group(s) from the form, use the group id to get the emails of all the people in the group(s)
        recipients = self.base.get_email_groups(data['groups'])
        # need to make sure these are actually here before trying to use them (isinstance)
        if isinstance(data['cc'], str):
            cc = self.base.get_emails(data['cc'])
        else:
            cc = ''

        if isinstance(data['bcc'], str):
            bcc = self.base.get_emails(data['bcc'])
        else:
            bcc = ''
        # need to check that all the stuff is actually filled in, if its not, we need to fill it with an empty value
        if self.base.send_message(data['subject'], data['message'], recipients, data['cc'], data['bcc']):
            return 'Success'
        return 'Failed'

    @route('/close-student', methods=['POST'])
    def close_session_student(self):  # this needs to be connected to the appointment end page
        data = request.form
        return self.base.close_session_student(data['appointment_id'])

    @route('/close-tutor', methods=['POST'])
    def close_session_tutor(self):  # this needs to be connected to the appointment end page
        data = request.form
        return self.base.close_session_tutor(data['appointment_id'], data['to_prof'])
