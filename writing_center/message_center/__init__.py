# Packages
from flask import render_template, request, redirect, url_for
from flask_classy import FlaskView, route

# Local
from writing_center import app


class MessageCenterView(FlaskView):
    route_base = 'message'

    def __init__(self):
        pass

    @route('/home')
    def index(self):
        return render_template('message_center/index.html', **locals())
