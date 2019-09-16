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
        """
        The reason the data is being made into a variable and then immediately copied is because
        it comes from the form as an immutable object. Meaning it cant be iterated through. 
        This is important, because when someone selects more than one group to send emails to, 
        they both come as data['recipients'] keys, but they're separate. By making this into a mutable object,
        we are able to iterate through and get all recipient groups. 
        """

        # grab the group(s) from the form, use the group id to get the emails of all the people in the group(s)
        if isinstance(data['recipients'], list):
            recipients = self.mcc.get_email_groups(data['recipients'])
        else:
            recipients = ''

        if isinstance(data['cc'], list):
            cc = self.mcc.get_emails(data['cc'])
        else:
            cc = ''

        if isinstance(data['bcc'], list):
            bcc = self.mcc.get_emails(data['bcc'])
        else:
            bcc = ''

        if self.mcc.send_message(data['subject'], data['message'], recipients, data['cc'], data['bcc']):
            return 'Success'
        return 'Failed'

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

    @route('/test', methods=['POST'])
    def test(self):
        data = request.form
        data_two = data.copy()  # makes the data into a mutable object so we can iterate through it

        groups = []
        for item in data_two.keys():  # iterate through the keys - need to figure out how to iterate all keys vs just unique keys
            print(item)
            if item == 'recipients':  # if our key is recipients, then we add the value to our list
                groups.append(data_two[item])  # adding the calue to our list
        # recipients = self.mcc.get_email_groups(data['recipients'])
        print(data_two)
        return ''
