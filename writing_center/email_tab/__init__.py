from flask_classy import FlaskView, route
from flask import render_template


class EmailView(FlaskView):
    def __init__(self):
        pass

    def index(self):
        return render_template('email_tab/test.html', **locals())
