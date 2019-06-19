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
        return render_template('message_center/index.html', **locals())

    @route('/send-message')
    def send_message(self):
        return render_template('message_center/send-message.html', **locals())

    @route('/message-preferences')
    def message_preferences(self):
        prefs = self.base.get_message_preferences()
        return render_template('message_center/preferences.html', **locals())

    def change_message_preferences(self):
        data = request.form.to_dict()
        return self.base.manage_message_preferences(data['substitute'], data['shift'])
