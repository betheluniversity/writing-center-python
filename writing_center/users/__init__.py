from flask_classy import FlaskView, route
from flask import render_template

class UsersView(FlaskView):
    def __init__(self):
        pass

    def manage_bans(self):
        return render_template('users/manage_bans.html', **locals())
