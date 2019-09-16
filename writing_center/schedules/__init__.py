from flask_classy import FlaskView, route, request
from flask import render_template, redirect, url_for, jsonify
from flask import session as flask_session
from datetime import datetime, date

import json

from writing_center.schedules.schedules_controller import SchedulesController
from writing_center.writing_center_controller import WritingCenterController
from writing_center.message_center.message_center_controller import MessageCenterController


class SchedulesView(FlaskView):
    route_base = '/schedules/'

    def __init__(self):
        self.sc = SchedulesController()
        self.wcc = WritingCenterController()
        self.mcc = MessageCenterController()

    @route("/create-schedule")
    def create_time_slot(self):
        self.wcc.check_roles_and_route(['Administrator'])
        schedules = self.sc.get_all_schedules()
        return render_template("schedules/create_time_slot.html", **locals())

    @route('/manage-tutor-schedules')
    def manage_tutor_schedules(self):
        self.wcc.check_roles_and_route(['Administrator'])
        schedules = self.sc.get_active_schedules()
        tutors = self.sc.get_active_tutors()
        time_setting = self.sc.get_time_setting()[0]
        return render_template('schedules/manage_tutor_schedules.html', **locals())

    @route('view-tutor-schedules')
    def view_tutor_schedules(self):
        self.wcc.check_roles_and_route(['Tutor', 'Administrator'])
        schedules = self.sc.get_active_schedules()
        tutors = self.sc.get_active_tutors()
        time_setting = self.sc.get_time_setting()[0]
        return render_template('schedules/view_tutor_schedule.html', **locals())

    @route('/create', methods=['POST'])
    def create_new_time_slot(self):
        self.wcc.check_roles_and_route(['Administrator'])
        form = request.form

        start_time = form.get('start-time')
        start_time = datetime.strftime(datetime.strptime(start_time, '%H:%M'), '%H:%M:%S')

        end_time = form.get('end-time')
        end_time = datetime.strftime(datetime.strptime(end_time, '%H:%M'), '%H:%M:%S')

        is_active = form.get('active')

        created = self.sc.create_time_slot(start_time, end_time, is_active)

        if created:
            self.wcc.set_alert('success', 'Schedule Created Successfully!')
        else:
            self.wcc.set_alert('danger', 'Schedule already exists!')
        return redirect(url_for('SchedulesView:create_time_slot'))

    @route('deactivate-time-slots', methods=['POST'])
    def deactivate_time_slots(self):
        self.wcc.check_roles_and_route(['Administrator'])
        form = request.form
        json_schedule_ids = form.get('jsonScheduleIds')
        schedule_ids = json.loads(json_schedule_ids)
        try:
            for schedule_id in schedule_ids:
                self.sc.deactivate_time_slot(schedule_id)
            self.wcc.set_alert('success', 'Time slot(s) deactivated successfully!')
        except Exception as error:
            self.wcc.set_alert('danger', 'Failed to deactivate time slot(s)')
        return 'done'  # Return doesn't matter: success or failure take you to the same page. Only the alert changes.

    @route('/add-tutors-to-shifts', methods=['POST'])
    def add_tutors_to_shifts(self):
        self.wcc.check_roles_and_route(['Administrator'])

        form = request.form

        start_date = form.get('start-date')
        end_date = form.get('end-date')
        if not start_date or not end_date:
            self.wcc.set_alert('danger', 'You must set a start date AND an end date!')
            return redirect(url_for('SchedulesView:manage_tutor_schedules'))
        # Formats the date strings into date objects
        start = datetime.strptime(start_date, '%a %b %d %Y').date()
        end = datetime.strptime(end_date, '%a %b %d %Y').date()
        if start > end:
            self.wcc.set_alert('danger', 'Start date cannot be further in the future than the end date!')
            return redirect(url_for('SchedulesView:manage_tutor_schedules'))
        multilingual = int(form.get('multilingual'))
        drop_in = int(form.get('drop-in'))
        tutors = form.getlist('tutors')
        days = form.getlist('days')
        time_slots = form.getlist('time-slots')

        if tutors[0] == 'Select All Tutors':
            tutors = []
            for tutor in self.sc.get_active_tutors():
                tutors.append(tutor.id)
        success = self.sc.create_tutor_shifts(start, end, multilingual, drop_in, tutors, days, time_slots)
        if not success:
            self.wcc.set_alert('warning', 'The shifts failed to be scheduled! One or more of the selected day of week never occurs.')
            return redirect(url_for('SchedulesView:manage_tutor_schedules'))
        if success == 'warning':
            self.wcc.set_alert('warning', 'One or more of the shifts failed to be scheduled.')
            return redirect(url_for('SchedulesView:manage_tutor_schedules'))
        self.wcc.set_alert('success', 'Successfully added the tutor(s) to the time slot(s).')
        return redirect(url_for('SchedulesView:manage_tutor_schedules'))

    @route('/show-schedule', methods=['POST'])
    def show_tutor_schedule(self):
        self.wcc.check_roles_and_route(['Administrator', 'Tutor'])
        names = json.loads(request.data).get('tutors')
        if 'view-all' in names:
            tutors = self.sc.get_active_tutors()
            names = []
            for tutor in tutors:
                names.append(str(tutor.id))
        all_tutor_appts = self.sc.get_tutor_appointments(names)
        appointments = []
        # Formats the times to match the fullcalendar desired format
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
                tutor = self.sc.get_user_by_id(appointment.tutor_id)
                appointments.append({
                    'id': appointment.id,
                    'studentId': appointment.student_id,
                    'tutorName': '{0} {1}'.format(tutor.firstName, tutor.lastName),
                    'startTime': start_time,
                    'endTime': end_time,
                    'multilingual': appointment.multilingual,
                    'dropIn': appointment.dropIn,
                    'sub': appointment.sub
                })
                
        return jsonify(appointments)

    @route('delete-confirmation', methods=['POST'])
    def confirm_delete(self):
        self.wcc.check_roles_and_route(['Administrator'])
        # Post method that displays a confirmation before appointments within a given range for selected tutors are
        # deleted to make sure the person knows what they are doing
        start_date = str(json.loads(request.data).get('startDate'))
        end_date = str(json.loads(request.data).get('endDate'))
        start = datetime.strptime(start_date, '%a %b %d %Y').date()
        end = datetime.strptime(end_date, '%a %b %d %Y').date()
        tutor_ids = json.loads(request.data).get('tutors')
        names = []
        if start > end:
            invalid_date = True
        if 'view-all' in tutor_ids:
            tutors = self.sc.get_active_tutors()
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
        self.wcc.check_roles_and_route(['Administrator'])
        appt_id = str(json.loads(request.data).get('appt_id'))
        deleted = self.sc.delete_appointment(appt_id)
        if deleted:
            if deleted == 'sub':
                return deleted
            else:
                return appt_id
        else:
            self.wcc.set_alert('danger', 'Failed to delete appointment!')
            return redirect(url_for('SchedulesView:manage_tutor_schedules'))

    @route('confirm-delete', methods=['post'])
    def confirm_delete_appointment(self):
        self.wcc.check_roles_and_route(['Administrator'])

        appt_id = str(json.loads(request.data).get('appt_id'))
        deleted = self.sc.confirm_delete_appointment(appt_id)
        if deleted:
            # TODO: probably should send an email here
            return appt_id
        else:
            self.wcc.set_alert('danger', 'Failed to delete appointment!')
            return redirect(url_for('SchedulesView:manage_tutor_schedules'))

    @route('delete-tutor-shifts', methods=['POST'])
    def delete_tutors_from_shifts(self):
        self.wcc.check_roles_and_route(['Administrator'])
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
            tutors = self.sc.get_active_tutors()
            tutor_ids = []
            for ids in tutors:
                tutor_ids.append(str(ids.id))
        sub_appts = self.sc.delete_tutor_shifts(tutor_ids, start, end)
        if sub_appts == 'none':
            return '<h3>All appointments in the selected range were deleted successfully!</h3>'
        if sub_appts:
            return render_template('schedules/sub_table.html', **locals(), id_to_user=self.sc.get_user_by_id)
        return '<h3>There weren\'t any appointments within the date range selected!</h3>'

    @route('request-sub', methods=['POST'])
    def request_sub(self):
        self.wcc.check_roles_and_route(['Administrator'])
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
        self.wcc.check_roles_and_route(['Student', 'Tutor', 'Administrator'])

        if flask_session['USERNAME'] in ['Student', 'Tutor', 'Administrator', 'Observer']:
            return ''

        appts = self.sc.get_all_user_appointments(flask_session['USERNAME'])
        appointments = []
        # Formats the times to match the fullcalendar desired format
        for appointment in appts:
            if appointment.actualStart and appointment.actualEnd:
                start_time = '{0}-{1}-{2}T{3}:{4}:{5}'.format(appointment.actualStart.year,
                                                              appointment.actualStart.strftime('%m'),
                                                              appointment.actualStart.strftime('%d'),
                                                              appointment.actualStart.strftime('%H'),
                                                              appointment.actualStart.strftime('%M'),
                                                              appointment.actualStart.strftime('%S'))
                end_time = '{0}-{1}-{2}T{3}:{4}:{5}'.format(appointment.actualEnd.year,
                                                            appointment.actualEnd.strftime('%m'),
                                                            appointment.actualEnd.strftime('%d'),
                                                            appointment.actualEnd.strftime('%H'),
                                                            appointment.actualEnd.strftime('%M'),
                                                            appointment.actualEnd.strftime('%S'))
            else:
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
            tutor = self.sc.get_user_by_id(appointment.tutor_id)
            appointments.append({
                'id': appointment.id,
                'studentId': appointment.student_id,
                'tutorName': '{0} {1}'.format(tutor.firstName, tutor.lastName),
                'startTime': start_time,
                'endTime': end_time,
                'multilingual': appointment.multilingual,
                'dropIn': appointment.dropIn,
                'sub': appointment.sub
            })

        return jsonify(appointments)

    def get_sub_appointments(self):
        self.wcc.check_roles_and_route(['Tutor', 'Administrator'])
        appts = self.sc.get_sub_appointments()
        appointments = []
        # Formats the times to match the fullcalendar desired format
        for appointment in appts:
            if appointment.actualStart and appointment.actualEnd:
                start_time = '{0}-{1}-{2}T{3}:{4}:{5}'.format(appointment.actualStart.year,
                                                              appointment.actualStart.strftime('%m'),
                                                              appointment.actualStart.strftime('%d'),
                                                              appointment.actualStart.strftime('%H'),
                                                              appointment.actualStart.strftime('%M'),
                                                              appointment.actualStart.strftime('%S'))
                end_time = '{0}-{1}-{2}T{3}:{4}:{5}'.format(appointment.actualEnd.year,
                                                            appointment.actualEnd.strftime('%m'),
                                                            appointment.actualEnd.strftime('%d'),
                                                            appointment.actualEnd.strftime('%H'),
                                                            appointment.actualEnd.strftime('%M'),
                                                            appointment.actualEnd.strftime('%S'))
            else:
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
            tutor = self.sc.get_user_by_id(appointment.tutor_id)
            appointments.append({
                'id': appointment.id,
                'studentId': appointment.student_id,
                'tutorName': '{0} {1}'.format(tutor.firstName, tutor.lastName),
                'startTime': start_time,
                'endTime': end_time,
                'multilingual': appointment.multilingual,
                'dropIn': appointment.dropIn,
                'sub': appointment.sub
            })

        return jsonify(appointments)

    @route('pickup-shift', methods=['POST'])
    def pickup_shift(self):
        self.wcc.check_roles_and_route(['Tutor', 'Administrator'])

        if flask_session['USERNAME'] in ['Administrator', 'Observer', 'Tutor', 'Student']:
            self.wcc.set_alert('danger', 'You cannot pick up a shift while acting as a role')
        else:

            appointment_id = str(json.loads(request.data).get('appt_id'))
            appt = self.sc.get_one_appointment(appointment_id)
            self.mcc.substitute_request_filled(appointment_id)
            # TODO MAYBE EMAIL STUDENT ABOUT TUTOR CHANGE IF APPLICABLE?
            picked_up = self.sc.pickup_shift(appointment_id, flask_session['USERNAME'])
            if picked_up:
                self.wcc.set_alert('success', 'Successfully picked up the shift!')
            else:
                self.wcc.set_alert('danger', 'Failed to pick up the shift.')

        return 'finished'

    @route('request-subtitute', methods=['POST'])
    def request_substitute(self):
        self.wcc.check_roles_and_route(['Tutor', 'Administrator'])
        appointment_id = str(json.loads(request.data).get('appt_id'))
        appt = self.sc.get_one_appointment(appointment_id)
        success = self.sc.request_substitute(appointment_id)
        if success:
            self.mcc.request_substitute(appointment_id)
            self.wcc.set_alert('success', 'Successfully requested a substitute!')
        else:
            self.wcc.set_alert('danger', 'Error! Substitute not requested.')
        return 'finished'
