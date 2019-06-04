from flask_classy import FlaskView, route
from flask import render_template


class StatisticsView(FlaskView):
    def __init__(self):
        pass

    def index(self):
        return render_template('statistics/index.html', **locals())

    @route('/center-manager/statistics/')
    def stats(self):
        return render_template('statistics/statistics.html', **locals())

    def stats_observer(self):
        return render_template('statistics/statistics_observer.html', **locals())

    def view_reports(self):
        return render_template()

    def hours_worked(self):
        return render_template('statistics/hours_worked.html', **locals())