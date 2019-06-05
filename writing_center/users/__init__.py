from flask_classy import FlaskView, route
from flask import render_template

class UsersView(FlaskView):
    def __init__(self):
        pass

    def index(self):
        return render_template('users/index.html', **locals())

    @route('/center-manager/manage-bans/')
    def manage_bans(self):
        return render_template('users/manage_bans.html', **locals())

    @route('/center-manager/view-users')
    def view_all_users(self):
        return render_template('users/view_all_users.html', **locals())