from flask_classy import FlaskView, route, request
from flask import render_template, redirect, url_for
from datetime import datetime

import json

from writing_center.schedules.schedules_controller import SchedulesController


class SchedulesView(FlaskView):
    route_base = '/schedules/'

    def __init__(self):
        self.sc = SchedulesController()

    @route("/create-schedule")
    def create_schedule(self):
        schedules = self.sc.get_schedules()
        tutors = self.sc.get_tutors()
        return render_template("schedules/create_schedule.html", **locals())

    @route('/center-manager/manage-tutor-schedules')
    def manage_tutor_schedules(self):
        return render_template('schedules/manage_tutor_schedules.html', **locals())

    def view_tutor_schedules(self):
        return render_template('schedules/view_tutor_schedule.html', **locals())

    @route('/create', methods=['post'])
    def create_new_schedule(self):
        now = (datetime.now())

        start_time = str(json.loads(request.data).get('startTime'))
        start_time = datetime.strptime(start_time, '%H:%M')
        start_time = start_time.replace(year=int(now.strftime('%Y')), month=int(now.strftime('%m')), day=int(now.strftime('%d')))

        end_time = str(json.loads(request.data).get('endTime'))
        end_time = datetime.strptime(end_time, '%H:%M')
        end_time = end_time.replace(year=int(now.strftime('%Y')), month=int(now.strftime('%m')), day=int(now.strftime('%d')))

        is_active = str(json.loads(request.data).get('isActive'))
        if is_active == 'Active':
            is_active = 'Yes'
        else:
            is_active = 'No'
        self.sc.create_schedule(start_time, end_time, is_active)
        return redirect(url_for('SchedulesView:create_schedule'))
