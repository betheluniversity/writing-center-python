from flask_classy import FlaskView, route, request
from flask import render_template, redirect, url_for, jsonify
from flask import session as flask_session
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

    @route('view-tutor-schedules')
    def view_tutor_schedules(self):
        schedules = self.sc.get_schedules()
        tutors = self.sc.get_tutors()
        time_setting = self.sc.get_time_setting()[0]
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
        if start_date == end_date:
            self.wcc.set_alert('danger', 'No Appointments Made! Start Date and End Date must be different days!')
            return redirect(url_for('SchedulesView:create_schedule'))
        multilingual = str(json.loads(request.data).get('multilingual'))
        drop_in = str(json.loads(request.data).get('dropIn'))
        tutors = json.loads(request.data).get('tutors')
        days = json.loads(request.data).get('days')
        time_slots = json.loads(request.data).get('timeSlots')

        if tutors[0] == 'select-all':
            tutors = []
            for tutor in self.sc.get_tutors():
                tutors.append(tutor.id)
        self.sc.create_tutor_shifts(start_date, end_date, multilingual, drop_in, tutors, days, time_slots)
        return redirect(url_for('SchedulesView:create_schedule'))

    @route('/show-schedule', methods=['POST'])
    def show_tutor_schedule(self):
        names = json.loads(request.data).get('tutors')
        if 'view-all' in names:
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
        # Post method that displays a confirmation before appointments within a given range for selected tutors are
        # deleted to make sure the person knows what they are doing
        start_date = str(json.loads(request.data).get('startDate'))
        end_date = str(json.loads(request.data).get('endDate'))
        start = datetime.strptime(start_date, '%a %b %d %Y').date()
        end = datetime.strptime(end_date, '%a %b %d %Y').date()
        tutor_ids = json.loads(request.data).get('tutors')
        names = []
        if start_date > end_date:
            invalid_date = True
        if 'view-all' in tutor_ids:
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

    @route('delete-appointment', methods=['POST'])
    def delete_appointment(self):
        appt_id = str(json.loads(request.data).get('appt_id'))
        deleted = self.sc.delete_appointment(appt_id)
        if deleted:
            if deleted == 'sub':
                return deleted
            else:
                return appt_id
        else:
            self.wcc.set_alert('danger', 'Failed to delete appointment!')
            return redirect(url_for('SchedulesView:view_tutor_schedules'))

    @route('delete-tutor-shifts', methods=['POST'])
    def delete_tutors_from_shifts(self):
        # Post method to delete appointments which selected tutors are running in a given date range
        start_date = str(json.loads(request.data).get('startDate'))
        end_date = str(json.loads(request.data).get('endDate'))
        start = datetime.strptime(start_date, '%a %b %d %Y').date()
        end = datetime.strptime(end_date, '%a %b %d %Y').date()

        # If start > end that means start is further into the future than end in so we should the confirmation html
        # again to tell them to fix that
        if start > end:
            invalid_date = True
            return render_template('schedules/delete_confirmation.html', **locals())

        # If we get past that check, then we delete the appointment(s) and show the substitution table
        tutor_ids = json.loads(request.data).get('tutors')
        if 'view-all' in tutor_ids:
            tutors = self.sc.get_tutors()
            tutor_ids = []
            for ids in tutors:
                tutor_ids.append(str(ids.id))
        sub_appts = self.sc.delete_tutor_shifts(tutor_ids, start, end)
        if not sub_appts:
            self.wcc.set_alert('danger', 'Failed to Delete Appointments!')
        return render_template('schedules/sub_table.html', **locals(), id_to_user=self.sc.get_user_by_id)

    @route('request-sub', methods=['POST'])
    def request_sub(self):
        # Post method to request a sub for a given appointment or subs for all given appointments
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

    @route('get-appointments', methods=['GET'])
    def get_users_appointments(self):
        appts = self.sc.get_all_user_appointments(flask_session['USERNAME'])
        appointments = []
        for appointment in appts:
            if appointment.actualStart and appointment.actualEnd:
                start_time = '{0}-{1}-{2}T{3}:{4}:{5}'.format(appointment.actualStart.year,
                                                              appointment.actualStart.strftime('%m'),
                                                              appointment.actualStart.strftime('%d'),
                                                              appointment.actualStart.strftime('%I'),
                                                              appointment.actualStart.strftime('%M'),
                                                              appointment.actualStart.strftime('%S'))
                end_time = '{0}-{1}-{2}T{3}:{4}:{5}'.format(appointment.actualEnd.year,
                                                            appointment.actualEnd.strftime('%m'),
                                                            appointment.actualEnd.strftime('%d'),
                                                            appointment.actualEnd.strftime('%I'),
                                                            appointment.actualEnd.strftime('%M'),
                                                            appointment.actualEnd.strftime('%S'))
            else:
                start_time = '{0}-{1}-{2}T{3}:{4}:{5}'.format(appointment.scheduledStart.year,
                                                              appointment.scheduledStart.strftime('%m'),
                                                              appointment.scheduledStart.strftime('%d'),
                                                              appointment.scheduledStart.strftime('%I'),
                                                              appointment.scheduledStart.strftime('%M'),
                                                              appointment.scheduledStart.strftime('%S'))
                end_time = '{0}-{1}-{2}T{3}:{4}:{5}'.format(appointment.scheduledEnd.year,
                                                            appointment.scheduledEnd.strftime('%m'),
                                                            appointment.scheduledEnd.strftime('%d'),
                                                            appointment.scheduledEnd.strftime('%I'),
                                                            appointment.scheduledEnd.strftime('%M'),
                                                            appointment.scheduledEnd.strftime('%S'))
            appointments.append({
                'id': appointment.id,
                'studentId': appointment.student_id,
                'tutorUsername': self.sc.get_user_by_id(appointment.tutor_id).username,
                'startTime': start_time,
                'endTime': end_time,
                'multilingual': appointment.multilingual,
                'dropIn': appointment.dropIn
            })

        return jsonify(appointments)

    def get_sub_appointments(self):
        appts = self.sc.get_sub_appointments()
        appointments = []
        for appointment in appts:
            if appointment.actualStart and appointment.actualEnd:
                start_time = '{0}-{1}-{2}T{3}:{4}:{5}'.format(appointment.actualStart.year,
                                                              appointment.actualStart.strftime('%m'),
                                                              appointment.actualStart.strftime('%d'),
                                                              appointment.actualStart.strftime('%I'),
                                                              appointment.actualStart.strftime('%M'),
                                                              appointment.actualStart.strftime('%S'))
                end_time = '{0}-{1}-{2}T{3}:{4}:{5}'.format(appointment.actualEnd.year,
                                                            appointment.actualEnd.strftime('%m'),
                                                            appointment.actualEnd.strftime('%d'),
                                                            appointment.actualEnd.strftime('%I'),
                                                            appointment.actualEnd.strftime('%M'),
                                                            appointment.actualEnd.strftime('%S'))
            else:
                start_time = '{0}-{1}-{2}T{3}:{4}:{5}'.format(appointment.scheduledStart.year,
                                                              appointment.scheduledStart.strftime('%m'),
                                                              appointment.scheduledStart.strftime('%d'),
                                                              appointment.scheduledStart.strftime('%I'),
                                                              appointment.scheduledStart.strftime('%M'),
                                                              appointment.scheduledStart.strftime('%S'))
                end_time = '{0}-{1}-{2}T{3}:{4}:{5}'.format(appointment.scheduledEnd.year,
                                                            appointment.scheduledEnd.strftime('%m'),
                                                            appointment.scheduledEnd.strftime('%d'),
                                                            appointment.scheduledEnd.strftime('%I'),
                                                            appointment.scheduledEnd.strftime('%M'),
                                                            appointment.scheduledEnd.strftime('%S'))
            appointments.append({
                'id': appointment.id,
                'studentId': appointment.student_id,
                'tutorUsername': self.sc.get_user_by_id(appointment.tutor_id).username,
                'startTime': start_time,
                'endTime': end_time,
                'multilingual': appointment.multilingual,
                'dropIn': appointment.dropIn
            })

        return jsonify(appointments)

    @route('load-appointment', methods=['POST'])
    def load_appointment_table(self):
        appointment_id = str(json.loads(request.data).get('id'))
        appt = self.sc.get_one_appointment(appointment_id)
        return render_template('schedules/appointment_information.html', **locals(),
                               id_to_user=self.sc.get_user_by_id)

    @route('pickup-shift', methods=['POST'])
    def pickup_shift(self):
        appointment_id = str(json.loads(request.data).get('appt_id'))
        appt = self.sc.get_one_appointment(appointment_id)
        # TODO MAYBE EMAIL STUDENT ABOUT TUTOR CHANGE IF APPLICABLE?
        picked_up = self.sc.pickup_shift(appointment_id, flask_session['USERNAME'])
        if picked_up:
            self.wcc.set_alert('success', 'Successfully picked up the shift!')
            return render_template('schedules/appointment_information.html', **locals(),
                                   id_to_user=self.sc.get_user_by_id)
        else:
            self.wcc.set_alert('danger', 'Failed to pick up the shift.')

    @route('request-subtitute', methods=['POST'])
    def request_substitute(self):
        appointment_id = str(json.loads(request.data).get('appt_id'))
        appt = self.sc.get_one_appointment(appointment_id)
        # TODO MAYBE EMAIL ABOUT SUB
        success = self.sc.request_substitute(appointment_id)
        if success:
            self.wcc.set_alert('success', 'Successfully requested a substitute!')
            return render_template('schedules/appointment_information.html', **locals(),
                                   id_to_user=self.sc.get_user_by_id)
        else:
            self.wcc.set_alert('danger', 'Error! Substitute not requested.')
