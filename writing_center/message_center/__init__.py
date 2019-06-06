# Packages
from flask import render_template, request, redirect, url_for
from flask_classy import FlaskView, route

# Local
from writing_center.message_center import message_center_controller


class MessageCenterView(FlaskView):
    route_base = 'message'

    def __init__(self):
        pass

    @route('/')
    def index(self):
        return render_template('message_center/index.html', **locals())

    @route('/send-message')
    def send_message(self):
        return render_template('message_center/send-message.html', **locals())

    @route('/message-preferences')
    def message_preferences(self):
        prefs = []
        prefs = message_center_controller.get_message_preferences()
        return render_template('message_center/preferences.html', **locals())

    def change_message_preferences(self):
        data = request.form.to_dict()
        return message_center_controller.manage_message_preferences(data['substitute'], data['shift'])
