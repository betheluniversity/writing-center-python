from flask_classy import FlaskView, route
from flask import render_template, request, redirect, url_for
from flask import session as flask_session
import json

from writing_center.profile.profile_controller import ProfileController
from writing_center.writing_center_controller import WritingCenterController
from writing_center.message_center.message_center_controller import MessageCenterController


class ProfileView(FlaskView):
    route_base = '/profile'

    def __init__(self):
        self.pc = ProfileController()
        self.wcc = WritingCenterController()
        self.mcc = MessageCenterController()

    @route('/edit')
    def index(self):
        self.wcc.check_roles_and_route(['Student', 'Tutor', 'Observer', 'Administrator'])
        user = self.pc.get_user_by_username(flask_session['USERNAME'])
        preferences = self.mcc.get_email_preferences()
        return render_template('profile/profile.html', **locals())

    @route('/save-edits', methods=['POST'])
    def save_edits(self):
        self.wcc.check_roles_and_route(['Student', 'Tutor', 'Observer', 'Administrator'])
        try:
            form = request.form
            first_name = form.get('first-name')
            last_name = form.get('last-name')
            username = form.get('username')

            if isinstance(form.get('shift'), str):  # if shift is there, the box is checked and should be set to true
                self.mcc.toggle_shift(1)
            else:  # otherwise, it should be set to false
                self.mcc.toggle_shift(0)

            if isinstance(form.get('substitute'), str):  # if sub is there, the box is checked and should be set to true
                self.mcc.toggle_substitute(1)
            else:  # otherwise, it should be set to false
                self.mcc.toggle_substitute(0)

            self.pc.edit_user(first_name,last_name, username)
            # Need to reset the users name, which appears in the upper right corner
            flask_session['NAME'] = '{0} {1}'.format(first_name, last_name)
            flask_session.modified = True
            self.wcc.set_alert('success', 'Your profile has been edited successfully!')
        except Exception as error:
            self.wcc.set_alert('danger', 'Failed to edit your profile: {0}'.format(str(error)))
        return redirect(url_for('ProfileView:index'))

    @route('/view-role')
    def role_viewer(self):
        self.wcc.check_roles_and_route(['Administrator'])
        role_list = self.pc.get_all_roles()
        return render_template('profile/role_viewer.html', **locals())

    @route('/change-role', methods=['POST'])
    def change_role(self):
        self.wcc.check_roles_and_route(['Administrator'])
        if not flask_session['ADMIN-VIEWER']:
            form = request.form
            role_id = form.get('role')
            role = self.pc.get_role(role_id)
            flask_session['ADMIN-VIEWER'] = True
            # Saving old info to return too
            flask_session['ADMIN-USERNAME'] = flask_session['USERNAME']
            flask_session['ADMIN-ROLES'] = flask_session['USER-ROLES']
            flask_session['ADMIN-NAME'] = flask_session['NAME']
            # Setting up viewing role
            flask_session['USERNAME'] = role.name
            flask_session['NAME'] = ""
            flask_session['USER-ROLES'] = role.name
        return redirect(url_for('View:index'))

    @route('/toggle-substitute', methods=['POST'])
    def toggle_substitute(self):
        self.wcc.check_roles_and_route(['Tutor', 'Observer', 'Administrator'])
        data = request.form
        return self.mcc.toggle_substitute(int(data['substitute']))

    @route('/toggle-shift', methods=['POST'])
    def toggle_shift(self):
        self.wcc.check_roles_and_route(['Tutor', 'Observer', 'Administrator'])
        data = request.form
        return self.mcc.toggle_shift(data['shift'])
