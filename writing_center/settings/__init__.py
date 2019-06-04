from flask_classy import FlaskView, route
from flask import render_template


class SettingsView(FlaskView):
    def __init__(self):
        pass

    @route('/')
    def index(self):
        return render_template('settings/index.html')
