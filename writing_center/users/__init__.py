from flask_classy import FlaskView, route, request
from flask import render_template, redirect, url_for

from writing_center.users.users_controller import UsersController
from writing_center.wsapi.wsapi_controller import WSAPIController

class UsersView(FlaskView):
    def __init__(self):
        self.uc = UsersController()
        self.wsapi = WSAPIController()

    def index(self):
        return render_template('users/index.html', **locals())

    @route('/center-manager/manage-bans/')
    def manage_bans(self):
        return render_template('users/manage_bans.html', **locals())

    @route('/center-manager/view-users')
    def view_all_users(self):
        users = self.uc.get_users()
        return render_template('users/view_all_users.html', **locals())

    @route("/center-manager/add-user")
    def add_user(self):
        return render_template('users/add_user.html', **locals())

    @route("/search-users", methods=['post'])
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

    @route('/create-user', methods=['post'])
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
            print('got here')
            # self.slc.set_alert('success', '{0} {1} ({2}) added successfully!'.format(first_name, last_name, username))
            return redirect(url_for('UsersView:view_all_users'))
        except Exception as error:
            # self.slc.set_alert('danger', 'Failed to add user: {0}'.format(str(error)))
            print(error)
            return redirect(url_for('UsersView:select_user_roles', username=username, first_name=first_name, last_name=last_name))

    @route("/admin/<int:user_id>")
    def edit_user(self, user_id):
        user = self.uc.get_user(user_id)
        roles = self.uc.get_all_roles()
        user_role_ids = self.uc.get_user_role_ids(user_id)

        return render_template('users/edit_user.html', **locals())

    @route("/save-user-edits", methods=['post'])
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
            print(error)
            return redirect(url_for('UsersView:edit_user', user_id=user_id))
