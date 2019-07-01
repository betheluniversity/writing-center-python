from flask_classy import FlaskView, route
from flask import render_template, request, redirect, url_for
from flask import session as flask_session
import json

from writing_center.profile.profile_controller import ProfileController
from writing_center.writing_center_controller import WritingCenterController


class ProfileView(FlaskView):
    route_base = '/profile'

    def __init__(self):
        self.pc = ProfileController()
        self.wcc = WritingCenterController()

    @route('/edit')
    def index(self):
        user = self.pc.get_user_by_username(flask_session['USERNAME'])
        return render_template('profile/profile.html', **locals())

    @route('/save-edits', methods=['post'])
    def save_edits(self):
        try:
            form = request.form
            first_name = form.get('first-name')
            last_name = form.get('last-name')
            username = form.get('username')
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
        role_list = self.pc.get_all_roles()
        return render_template('profile/role_viewer.html', **locals())

    @route('/change-role', methods=['POST'])
    def change_role(self):
        if not flask_session['ADMIN-VIEWER']:
            role = str(json.loads(request.data).get('chosen-role'))
            flask_session['ADMIN-VIEWER'] = True
            # Saving old info to return too
            flask_session['ADMIN-USERNAME'] = flask_session['USERNAME']
            flask_session['ADMIN-ROLES'] = flask_session['USER-ROLES']
            flask_session['ADMIN-NAME'] = flask_session['NAME']
            # Setting up viewing role
            flask_session['USERNAME'] = role
            flask_session['NAME'] = ""
            flask_session['USER-ROLES'] = role
        return redirect(url_for('ProfileView:role_viewer'))
