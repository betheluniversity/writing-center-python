from flask import render_template
from flask_classy import FlaskView


class View(FlaskView):

    def index(self):
        temp = "This is a jinja variable"
        return render_template('index.html', **locals())
