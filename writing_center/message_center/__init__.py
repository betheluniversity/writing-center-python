# Packages
from flask import render_template, request, redirect, url_for
from flask_classy import FlaskView, route

# Local
from writing_center import app
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
        # need to check that all the stuff is actually filled in, if its not, I need to fill it with an empty value

        return self.base.send_message(data['subject'], data['message'], data['recipients'], data['cc'], data['bcc'])
