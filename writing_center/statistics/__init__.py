from flask_classy import FlaskView, route
from flask import render_template


class StatisticsView(FlaskView):
    def __init__(self):
        pass

    def index(self):
        return render_template('statistics/statistics.html', **locals())