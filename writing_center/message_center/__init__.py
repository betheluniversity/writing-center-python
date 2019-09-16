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
        # make sure there are no duplicates in the email list
        # need to check that all the stuff is actually filled in, if its not, we need to fill it with an empty value
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
