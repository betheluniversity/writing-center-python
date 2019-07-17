from flask_classy import FlaskView, route, request
from flask import render_template, redirect, url_for, jsonify
from datetime import datetime, date

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
        schedules = self.sc.get_schedules()
        tutors = self.sc.get_tutors()
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

        if created:
            self.wcc.set_alert('success', 'Schedule Created Successfully!')
        else:
            self.wcc.set_alert('danger', 'Schedule already exists!')
        return self.sc.get_schedules()

    @route('/add-tutors-to-shifts', methods=['POST'])
    def add_tutors_to_shifts(self):
        start_date = str(json.loads(request.data).get('startDate'))
        end_date = str(json.loads(request.data).get('endDate'))
        # Formats the date strings into date objects
        start_date = datetime.strptime(start_date, '%a %b %d %Y').date()
        end_date = datetime.strptime(end_date, '%a %b %d %Y').date()
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
        names = json.loads(request.data).get('tutors')
        if names[0] == 'view-all':
            tutors = self.sc.get_tutors()
            names = []
            for tutor in tutors:
                names.append(str(tutor.id))
        all_tutor_appts = self.sc.get_tutor_appointments(names)
        appointments = []
        for tutor_appts in all_tutor_appts:
            for appointment in tutor_appts:
                start_time = '{0}-{1}-{2}T{3}:{4}:{5}'.format(appointment.scheduledStart.year,
                                                              appointment.scheduledStart.strftime('%m'),
                                                              appointment.scheduledStart.strftime('%d'),
                                                              appointment.scheduledStart.strftime('%H'),
                                                              appointment.scheduledStart.strftime('%M'),
                                                              appointment.scheduledStart.strftime('%S'))
                end_time = '{0}-{1}-{2}T{3}:{4}:{5}'.format(appointment.scheduledEnd.year,
                                                            appointment.scheduledEnd.strftime('%m'),
                                                            appointment.scheduledEnd.strftime('%d'),
                                                            appointment.scheduledEnd.strftime('%H'),
                                                            appointment.scheduledEnd.strftime('%M'),
                                                            appointment.scheduledEnd.strftime('%S'))
                appointments.append({
                    'id': appointment.id,
                    'studentId': appointment.student_id,
                    'tutorId': appointment.tutor_id,
                    'startTime': start_time,
                    'endTime': end_time,
                    'multilingual': appointment.multilingual,
                    'dropIn': appointment.dropIn
                })
                
        return jsonify(appointments)

    @route('delete-confirmation', methods=['POST'])
    def confirm_delete(self):
        start_date = str(json.loads(request.data).get('startDate'))
        end_date = str(json.loads(request.data).get('endDate'))
        start = datetime.strptime(start_date, '%a %b %d %Y').date()
        end = datetime.strptime(end_date, '%a %b %d %Y').date()
        tutor_ids = json.loads(request.data).get('tutors')
        names = []
        invalid_date = False
        if start_date > end_date:
            invalid_date = True
        if tutor_ids[0] == 'view-all':
            tutors = self.sc.get_tutors()
            for tutor in tutors:
                user = self.sc.get_user_by_id(tutor.id)
                name = '{0} {1}'.format(user.firstName, user.lastName)
                names.append(name)
        else:
            for tutor_id in tutor_ids:
                user = self.sc.get_user_by_id(tutor_id)
                if user:
                    name = '{0} {1}'.format(user.firstName, user.lastName)
                    names.append(name)

        return render_template('schedules/delete_confirmation.html', **locals())

    @route('delete-tutor-shifts', methods=['POST'])
    def delete_tutors_from_shifts(self):
        start_date = str(json.loads(request.data).get('startDate'))
        end_date = str(json.loads(request.data).get('endDate'))
        start_date = datetime.strptime(start_date, '%a %b %d %Y').date()
        end_date = datetime.strptime(end_date, '%a %b %d %Y').date()

        if start_date > end_date:
            self.wcc.set_alert('danger', 'Shifts NOT Deleted! End Date Was Less Than Start Date!')
            return redirect(url_for('SchedulesView:show_tutor_schedule'))

        tutor_ids = json.loads(request.data).get('tutors')
        if tutor_ids[0] == 'view-all':
            tutors = self.sc.get_tutors()
            tutor_ids = []
            for ids in tutors:
                tutor_ids.append(str(ids.id))
        sub_appts = self.sc.delete_tutor_shifts(tutor_ids, start_date, end_date)
        return render_template('schedules/sub_table.html', **locals())

    @route('request-sub', methods=['POST'])
    def request_sub(self):
        appt_id = json.loads(request.data).get('apptID')
        appt_id_list = json.loads(request.data).get('apptIDList')
        if appt_id == 'all':
            worked = self.sc.sub_all(appt_id_list)
            if not worked:
                self.wcc.set_alert('danger', 'Failed to request a substitute for all appointments')
        else:
            worked = self.sc.request_substitute(appt_id)
            if not worked:
                self.wcc.set_alert('danger', 'Failed to request a substitute for appointment id {0}'.format(appt_id))
        return 'Substitute Requested Successfully'
