from flask_classy import FlaskView, route
from flask import render_template

class UsersView(FlaskView):
    def __init__(self):
        pass

    def index(self):
        render_template('users/test.html', **locals())
