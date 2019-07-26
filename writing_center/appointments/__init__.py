from flask_classy import FlaskView, route, request
from flask import render_template, jsonify, json, redirect, url_for
from flask import session as flask_session
from datetime import datetime, timedelta

from writing_center.appointments.appointments_controller import AppointmentsController
from writing_center.writing_center_controller import WritingCenterController
from writing_center.wsapi.wsapi_controller import WSAPIController


class AppointmentsView(FlaskView):
    route_base = 'appointments'

    def __init__(self):
        self.ac = AppointmentsController()
        self.wcc = WritingCenterController()
        self.wsapi = WSAPIController()

    def view_appointments(self):
        return render_template('appointments/view_appointments.html', **locals())

    @route('load-appointments', methods=['POST'])
    def load_appointments(self):
        dates = json.loads(request.data).get('dates')
        schedule_appt = json.loads(request.data).get('scheduleAppt')
        start = dates['start']
        end = dates['end']
        start = start.replace("T", " ").split(" ")[0]
        start = datetime.strptime(start, '%Y-%m-%d')
        end = end.replace("T", " ").split(" ")[0]
        end = datetime.strptime(end, '%Y-%m-%d').date() - timedelta(days=1)
        end = datetime.combine(end, datetime.max.time())

        if schedule_appt:
            time_limit = int(self.ac.get_time_limit()[0])
            range_appointments = self.ac.get_open_appointments_in_range(start, end, time_limit)
        else:
            range_appointments = self.ac.get_appointments_in_range(start, end)
        appointments = []
        if range_appointments:
            for appointment in range_appointments:
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

    @route('load-appointment', methods=['POST'])
    def load_appointment_table(self):
        appointment_id = str(json.loads(request.data).get('id'))
        schedule_appt = json.loads(request.data).get('scheduleAppt')
        appt = self.ac.get_one_appointment(appointment_id)

        return render_template('appointments/appointment_information.html', **locals(),
                               id_to_user=self.ac.get_user_by_id)

    def appointments_and_walk_ins(self):
        tutor = flask_session['USERNAME']
        appointments = self.ac.get_scheduled_appointments(tutor)
        users = {}
        for appt in appointments:
            user = self.ac.get_user_by_id(appt.student_id)
            if user != None:
                name = '{0} {1}'.format(user.firstName, user.lastName)
            else:
                name = ""
            users.update({appt.student_id: name})
        return render_template('appointments/appointments_and_walk_ins.html', **locals())

    def search_appointments(self):
        students = self.ac.get_users_by_role("Student")
        tutors = self.ac.get_users_by_role("Tutor")
        profs = self.ac.get_profs()
        courses = self.ac.get_courses()
        return render_template('appointments/search_appointments.html', **locals())

    def create_appointment(self):
        return render_template('appointments/create_appointment.html', **locals())

    @route('view-appointments')
    def student_view_appointments(self):
        return render_template('appointments/student_view_appointments.html', **locals())

    @route('get_appointments', methods=['GET'])
    def get_users_appointments(self):
        appts = self.ac.get_all_user_appointments(flask_session['USERNAME'])
        appointments = []
        for appointment in appts:
            if appointment.actualStart:
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
                'tutorId': appointment.tutor_id,
                'startTime': start_time,
                'endTime': end_time,
                'multilingual': appointment.multilingual,
                'dropIn': appointment.dropIn
            })

        return jsonify(appointments)

    @route('schedule-appointment', methods=['POST'])
    def schedule_appointment(self):
        appt_id = str(json.loads(request.data).get('appt_id'))
        username = flask_session['USERNAME']
        user = self.ac.get_user_by_username(username)
        if not user.bannedDate:
            appt_limit = int(self.ac.get_appointment_limit()[0])
            user_appointments = self.ac.get_future_user_appointments(user.id)
            if len(user_appointments) < appt_limit:
                roles = self.wsapi.get_roles_for_username(username)
                cas = False
                for role in roles:
                    if 'STUDENT-CAS' == roles[role]['userRole']:
                        cas = True
                if cas:
                    appt = self.ac.get_appointment_by_id(appt_id)
                    already_scheduled = False
                    for appointment in user_appointments:
                        if appointment.scheduledStart <= appt.scheduledStart <= appointment.scheduledEnd or \
                                appointment.scheduledStart <= appt.scheduledEnd <= appointment.scheduledEnd:
                            already_scheduled = True
                    if already_scheduled:
                        self.wcc.set_alert('danger', 'Failed to schedule appointment! You already have an appointment '
                                                     'that overlaps with the one you are trying to schedule.')
                    else:
                        # pass
                        appt = self.ac.create_appointment(appt_id)
                        if appt:
                            self.wcc.set_alert('success', 'Your Appointment Has Been Scheduled! To View Your '
                                                          'Appointments, Go To The "View Your Appointments" Page!')
                        else:
                            self.wcc.set_alert('danger', 'Error! Appointment Not Scheduled!')
                else:
                    # TODO MAYBE GIVE THEM A SPECIFIC EMAIL TO EMAIL?
                    self.wcc.set_alert('danger', 'Appointment NOT scheduled! Only CAS students can schedule'
                                                 ' appointments here. If you wish to schedule an appointment email a'
                                                 ' Writing Center Administrator.')
            else:
                self.wcc.set_alert('danger', 'Failed to schedule appointment. You already have ' + appt_limit +
                                   ' appointments scheduled and can\'t schedule any more.')
        else:
            # TODO MAYBE GIVE THEM A SPECIFIC EMAIL TO EMAIL?
            self.wcc.set_alert('danger', 'You are banned from making appointments! If you have any questions email a'
                                         ' Writing Center Administrator.')

        return appt_id

    @route('/begin-appointment', methods=['POST'])
    def begin_walk_in_appt(self):
        form = request.form
        username = form.get('username')
        user = self.ac.get_user_by_username(username)
        if user:
            self.ac.begin_appointment(username)
            self.wcc.set_alert('success', 'Appointment for ' + user.firstName + ' ' + user.lastName + ' started')
        else:
            self.wcc.set_alert('danger', 'Username ' + username + ' doesn\'t exist in Writing Center')
        return redirect(url_for('AppointmentsView:appointments_and_walk_ins'))

    @route('/handle-scheduled-appointments', methods=['POST'])
    def handle_scheduled_appointments(self):
        btn_id = str(json.loads(request.data).get('id'))
        appt_id = str(json.loads(request.data).get('value'))
        if btn_id == 'start':
            appt = self.ac.start_appointment(appt_id)
            if appt:
                self.wcc.set_alert('success', 'Appointment Started Successfully!')
            else:
                self.wcc.set_alert('danger', 'Appointment Failed To Start.')
        elif btn_id == 'continue':
            appt = self.ac.continue_appointment(appt_id)
            if appt:
                self.wcc.set_alert('success', 'Appointment Successfully Re-started!')
            else:
                self.wcc.set_alert('danger', 'Appointment Failed To Continue!')
        elif btn_id == 'end':
            appt = self.ac.end_appointment(appt_id)
            if appt:
                self.wcc.set_alert('success', 'Successfully Ended Appointment')
            else:
                self.wcc.set_alert('danger', 'Failed To End Appointment')
        elif btn_id == 'no-show':
            appt = self.ac.mark_no_show(appt_id)
            if appt:
                appointment = self.ac.get_user_by_appt(appt_id)
                user = self.ac.get_user_by_id(appointment.student_id)
                message = '{0} {1} Marked As No Show'.format(user.firstName, user.lastName)
                self.wcc.set_alert('success', message)
            else:
                self.wcc.set_alert('danger', 'Failed To Set As No Show')
        return redirect(url_for('AppointmentsView:appointments_and_walk_ins'))

    @route('/search', methods=['POST'])
    def search(self):
        form = request.form
        student = None if form.get('student') == 'None' else int(form.get('student'))
        tutor = None if form.get('tutor') == 'None' else int(form.get('tutor'))
        prof = None if form.get('prof') == 'None' else form.get('prof')
        course = None if form.get('course') == 'None' else form.get('course')
        start = None if form.get('start') == '' else form.get('start')
        end = None if form.get('end') == '' else form.get('end')
        if student is None and tutor is None and prof is None and course is None and start is None and end is None:
            return 'Please enter parameters to search by.'
        appointments = self.ac.search_appointments(student, tutor, prof, course, start, end)
        return render_template('appointments/appointment_search_table.html', **locals())
