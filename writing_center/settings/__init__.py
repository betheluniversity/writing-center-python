from flask_classy import FlaskView, route
from flask import render_template

from writing_center.settings.settings_controller import SettingsController


class SettingsView(FlaskView):
    def __init__(self):
        self.sc = SettingsController()

    @route('/')
    def index(self):
        settings = self.sc.get_settings()
        return render_template('settings/index.html', **locals())
