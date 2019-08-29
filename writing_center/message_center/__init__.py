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
        immutable_data = request.form
        data = immutable_data.copy()
        # grab the group(s) from the form, use the group id to get the emails of all the people in the group(s)
        if isinstance(data['recipients'], list):
            recipients = self.base.get_email_groups(data['recipients'])
        else:
            recipients = ''

        if isinstance(data['cc'], list):
            cc = self.base.get_emails(data['cc'])
        else:
            cc = ''

        if isinstance(data['bcc'], list):
            bcc = self.base.get_emails(data['bcc'])
        else:
            bcc = ''

        # (this should really be in the form) - checks to make sure we're sending the email to someone
        if recipients == '' and cc == '' and bcc == '':
            return 'No recipients'

        # need to check that all the stuff is actually filled in (ideally should be in the form), if its not, we need to fill it with an empty value
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

    @route('/okay', methods=['POST'])
    def okay(self):
        data = request.form
        data_two = data.copy()

        groups = [data_two['recipients']]
        # for item in data_two.keys():
        #     if item == 'recipients':
        #         groups.append(item)
        recipients = self.base.get_email_groups(data['recipients'])
        print(data_two)
        return ''
