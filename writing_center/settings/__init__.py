from flask_classy import FlaskView, route
from flask import render_template, request, redirect, url_for

from writing_center.writing_center_controller import WritingCenterController
from writing_center.settings.settings_controller import SettingsController


class SettingsView(FlaskView):
    def __init__(self):
        self.sc = SettingsController()
        self.wcc = WritingCenterController()

    @route('/')
    def index(self):
        self.wcc.check_roles_and_route(['Administrator'])
        settings = self.sc.get_settings()
        return render_template('settings/index.html', **locals())

    @route('change-settings', methods=['POST'])
    def change_settings(self):
        self.wcc.check_roles_and_route(['Administrator'])
        form = request.form
        setting_name = form.get('setting_name')
        new_setting = form.get('new_setting')
        try:
            self.sc.update_setting(setting_name, new_setting)
            self.wcc.set_alert('success', 'Settings updated successfully!')
            return 'success'
        except Exception as error:
            self.wcc.set_alert('danger', 'Failed to update settings: {0}'.format(str(error)))
            return 'failed'

    @route('cleanse', methods=['get'])
    def cleanse(self):
        self.wcc.check_roles_and_route(['Administrator'])
        try:
            self.sc.cleanse()
            self.wcc.set_alert('success', 'System cleansed successfully!')
        except Exception as error:
            self.wcc.set_alert('danger', 'Failed to cleanse system: {0}'.format(str(error)))
        return redirect(url_for('SettingsView:index'))
