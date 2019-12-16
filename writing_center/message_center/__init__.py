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
        # make sure there are no duplicates in the email list
        # need to check that all the stuff is actually filled in, if its not, we need to fill it with an empty value
        subject = data.get('subject')
        message = data.get('message')
        groups = data.getlist('recipients')
        cc_ids = data.getlist('cc')
        bcc_ids = data.getlist('bcc')

        recipients = self.base.get_cc(cc_ids)
        bcc = self.base.get_bcc(groups, bcc_ids)

        if self.base.send_message(subject, message, recipients, bcc, False):
            self.wcc.set_alert('success', 'Email sent successfully!')
        else:
            self.wcc.set_alert('danger', 'Email failed to send.')
        return redirect(url_for('MessageCenterView:index'))
