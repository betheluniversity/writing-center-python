from flask import render_template
from flask_classy import FlaskView, route


class SettingsView(FlaskView):
    def __init__(self):
        pass

    @route('/')
    def index(self):
        return render_template('settings/index.html')
