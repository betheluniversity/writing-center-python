from flask_classy import FlaskView, route
from flask import render_template


class SchedulesView(FlaskView):
    def __init__(self):
        pass

    @route("/create")
    def create_schedule(self):
        return render_template("schedules/create_schedule.html")
