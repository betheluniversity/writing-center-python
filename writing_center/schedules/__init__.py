from flask_classy import FlaskView, route
from flask import render_template


class SchedulesView(FlaskView):
    def __init__(self):
        pass

    @route("/create")
    def create_schedule(self):
        return render_template("schedules/create_schedule.html")

    @route('/center-manager/manage-tutor-schedules')
    def manage_tutor_schedules(self):
        return render_template('schedules/manage_tutor_schedules.html', **locals())
