from flask_classy import FlaskView, route, request
from flask import render_template, redirect, url_for, jsonify
from datetime import datetime

import json

from writing_center.schedules.schedules_controller import SchedulesController
from writing_center.writing_center_controller import WritingCenterController


class SchedulesView(FlaskView):
    route_base = '/schedules/'

    def __init__(self):
        self.sc = SchedulesController()
        self.wcc = WritingCenterController()

    @route("/create-schedule")
    def create_schedule(self):
        schedules = self.sc.get_schedules()
        tutors = self.sc.get_tutors()
        return render_template("schedules/create_schedule.html", **locals())

    @route('/manage-tutor-schedules')
    def manage_tutor_schedules(self):
        schedules = self.sc.get_schedules()
        tutors = self.sc.get_tutors()
        return render_template('schedules/manage_tutor_schedules.html', **locals())

    def view_tutor_schedules(self):
        return render_template('schedules/view_tutor_schedule.html', **locals())

    @route('/create', methods=['POST'])
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
        created = self.sc.create_schedule(start_time, end_time, is_active)

        # if created:
            # TODO SUCCESS MESSAGE
        # else:
            # TODO ERROR MESSAGE
        return self.sc.get_schedules()

    @route('/add-tutors-to-shifts', methods=['POST'])
    def add_tutors_to_shifts(self):
        start_date = str(json.loads(request.data).get('startDate'))
        end_date = str(json.loads(request.data).get('endDate'))
        # TODO IF START_DATE AND END_DATE ARE EQUAL SET DANGER MESSAGE AND RETURN TO PAGE
        if start_date == end_date:
            self.wcc.set_alert('danger', 'No Appointments Made! Start Date and End Date must be different days!')
        multilingual = str(json.loads(request.data).get('multilingual'))
        drop_in = str(json.loads(request.data).get('dropIn'))
        tutors = str(json.loads(request.data).get('tutors'))
        days = str(json.loads(request.data).get('days'))
        time_slots = str(json.loads(request.data).get('timeSlots'))
        # TODO IF TUTORS, DAYS, OR TIME_SLOTS ARE EMPTY THEN RETURN TO PAGE
        self.sc.create_tutor_shifts(start_date, end_date, multilingual, drop_in, tutors, days, time_slots)
        return redirect(url_for('SchedulesView:create_schedule'))

    @route('/show-schedule', methods=['POST'])
    def show_tutor_schedule(self):
        name = str(json.loads(request.data).get('tutorName'))
        tut_appts = self.sc.get_tutor_appointments(name)
        appointments = []
        for appointment in tut_appts:
            start_time = '{0}-{1}-{2}T{3}:{4}:{5}'.format(appointment.StartTime.year,
                                                          appointment.StartTime.strftime('%m'),
                                                          appointment.StartTime.strftime('%d'),
                                                          appointment.StartTime.strftime('%I'),
                                                          appointment.StartTime.strftime('%M'),
                                                          appointment.StartTime.strftime('%S'))
            end_time = '{0}-{1}-{2}T{3}:{4}:{5}'.format(appointment.EndTime.year, appointment.EndTime.strftime('%m'),
                                                        appointment.EndTime.strftime('%d'),
                                                        appointment.EndTime.strftime('%I'),
                                                        appointment.EndTime.strftime('%M'),
                                                        appointment.EndTime.strftime('%S'))
            appointments.append({
                'id': appointment.ID,
                'studentUsername': appointment.StudUsername,
                'tutorUsername': appointment.TutorUsername,
                'startTime': start_time,
                'endTime': end_time,
                'multilingual': appointment.multilingual,
                'dropIn': appointment.DropInAppt
            })
        print(appointments)
        return jsonify(appointments)
