from flask_classy import FlaskView, route, request
from flask import render_template, redirect, url_for
from flask import session as flask_session

import json

from writing_center.users.users_controller import UsersController
from writing_center.wsapi.wsapi_controller import WSAPIController
from writing_center.writing_center_controller import WritingCenterController


class UsersView(FlaskView):
    route_base = '/user'

    def __init__(self):
        self.uc = UsersController()
        self.wsapi = WSAPIController()
        self.wcc = WritingCenterController()

    def index(self):
        return render_template('users/index.html', **locals())

    @route('/center-manager/manage-bans/')
    def manage_bans(self):
        users = self.uc.get_banned_users()

        return render_template('users/manage_bans.html', **locals())

    @route('/center-manager/view-users')
    def view_all_users(self):
        users = self.uc.get_users()
        return render_template('users/view_all_users.html', **locals())

    @route("/center-manager/add-user")
    def add_user(self):
        return render_template('users/add_user.html', **locals())

    @route("/search-users", methods=['POST'])
    def search_users(self):
        form = request.form
        first_name = form.get('firstName')
        last_name = form.get('lastName')
        results = self.wsapi.get_username_from_name(first_name, last_name)
        return render_template('users/user_search_results.html', **locals())

    @route('/create/<username>/<first_name>/<last_name>')
    def select_user_roles(self, username, first_name, last_name):
        roles = self.uc.get_all_roles()
        existing_user = self.uc.get_user_by_username(username)
        if existing_user:  # User exists in system
            if 1 == 0:
                pass
            # TODO ADD IN deletedAt attribute in DB
            # if existing_user.deletedAt:  # Has been deactivated in the past
        #         self.user.activate_existing_user(username)
        #         message = "This user has been deactivated in the past, but now they are reactivated with their same roles."
            else:  # Currently active
                message = "This user already exists in the system and is activated."
        return render_template('users/select_user_roles.html', **locals())

    @route('/create-user', methods=['POST'])
    def create_user(self):
        form = request.form
        first_name = form.get('first-name')
        last_name = form.get('last-name')
        username = form.get('username')
        roles = form.getlist('roles')
        sub_email_pref = 0  # Default sending emails to No
        stu_email_pref = 0  # Default sending emails to No
        # If the user is a administrator or a professor, they get emails.
        if 'Global Admin' in roles or 'Administrator' in roles or 'Center Manager' in roles:
            sub_email_pref = 1
            stu_email_pref = 1
        if 'tutor' in roles:
            stu_email_pref = 1
        try:
            self.uc.create_user(first_name, last_name, username, sub_email_pref, stu_email_pref)
            self.uc.set_user_roles(username, roles)
            self.wcc.set_alert('success', '{0} {1} ({2}) added successfully!'.format(first_name, last_name, username))
            return redirect(url_for('UsersView:view_all_users'))
        except Exception as error:
            self.wcc.set_alert('danger', 'Failed to add user: {0}'.format(str(error)))
            return redirect(url_for('UsersView:select_user_roles', username=username, first_name=first_name, last_name=last_name))

    @route("/edit/<int:user_id>")
    def edit_user(self, user_id):
        user = self.uc.get_user(user_id)
        roles = self.uc.get_all_roles()
        user_role_ids = self.uc.get_user_role_ids(user_id)

        return render_template('users/edit_user.html', **locals())

    @route("/save-user-edits", methods=['POST'])
    def save_user_edits(self):
        form = request.form
        user_id = form.get('user-id')
        username = form.get('username')
        first_name = form.get('first-name')
        last_name = form.get('last-name')
        email = form.get('email')
        roles = form.getlist('roles')
        try:
            self.uc.update_user_info(user_id, first_name, last_name, email)
            self.uc.clear_current_roles(user_id)
            self.uc.set_user_roles(username, roles)
            return redirect(url_for('UsersView:view_all_users'))
        except Exception as error:
            return redirect(url_for('UsersView:edit_user', user_id=user_id))

    @route("/remove-ban/", methods=['POST'])
    def remove_ban(self):
        user_id = str(json.loads(request.data).get('id'))
        self.uc.remove_user_ban(user_id)
        return redirect(url_for('UsersView:manage_bans'))

    @route("/unban-all", methods=['POST'])
    def remove_all_bans(self):
        self.uc.remove_all_bans()
        return redirect(url_for('UsersView:manage_bans'))

    @route('/search-ban-users', methods=['POST'])
    def search_ban_users(self):
        form = request.form
        first_name = form.get('firstName')
        last_name = form.get('lastName')
        user = self.uc.get_user_by_name(first_name, last_name)
        return render_template('users/user_ban_search_results.html', **locals())

    @route('/ban/user/', methods=['POST'])
    def save_user_ban(self):
        form = request.form
        username = form.get('username')
        self.uc.ban_user(username)
        return redirect(url_for('UsersView:manage_bans'))

    def act_as_user(self, user_id):
        if not flask_session['ADMIN-VIEWER']:
            user_info = self.uc.get_user(user_id)
            flask_session['ADMIN-VIEWER'] = True
            # Saving old info to return to
            flask_session['ADMIN-USERNAME'] = flask_session['USERNAME']
            flask_session['ADMIN-ROLES'] = flask_session['USER-ROLES']
            flask_session['ADMIN-NAME'] = flask_session['NAME']
            # Setting up viewing role
            flask_session['USERNAME'] = user_info.username
            flask_session['NAME'] = '{0} {1}'.format(user_info.firstName, user_info.lastName)
            flask_session['USER-ROLES'] = []
            user_roles = self.uc.get_user_roles(user_info.id)
            for role in user_roles:
                flask_session['USER-ROLES'].append(role.name)
        return redirect(url_for('View:index'))

    @route('/reset-act-as', methods=['POST'])
    def reset_act_as(self):
        if flask_session['ADMIN-VIEWER']:
            try:
                # Resetting info
                flask_session['USERNAME'] = flask_session['ADMIN-USERNAME']
                flask_session['ADMIN-VIEWER'] = False
                flask_session['NAME'] = flask_session['ADMIN-NAME']
                flask_session['USER-ROLES'] = flask_session['ADMIN-ROLES']
                # Clearing out unneeded variables
                flask_session.pop('ADMIN-USERNAME')
                flask_session.pop('ADMIN-ROLES')
                flask_session.pop('ADMIN-NAME')
                return redirect(url_for('View:index'))
            except Exception as error:
                self.wcc.set_alert('danger', 'An error occurred: {0}'.format(str(error)))
                return redirect(url_for('View:index'))
        else:
            self.wcc.set_alert('danger', 'You do not have permission to access this function')
            return redirect(url_for('View:index'))

    # This method deactivates users both from view_all_users and edit_user
    @route('/deactivate/<int:user_id>', methods=['POST', 'GET'])
    def deactivate_user(self, user_id):
        try:
            self.uc.deactivate_user(user_id)
            self.wcc.set_alert('success', 'Users deactivated successfully!')
            return redirect(url_for("UsersView:view_all_users"))
        except Exception as e:
            self.wcc.set_alert('danger', 'Failed to deactivate user(s)')
            return redirect(url_for("UsersView:edit", user_id=user_id))
