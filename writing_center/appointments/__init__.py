from flask_classy import FlaskView, route, request
from flask import render_template, jsonify, json, redirect, url_for
from flask import session as flask_session
from datetime import datetime, timedelta

from writing_center.appointments.appointments_controller import AppointmentsController
from writing_center.writing_center_controller import WritingCenterController
from writing_center.message_center import MessageCenterController
from writing_center.wsapi.wsapi_controller import WSAPIController


class AppointmentsView(FlaskView):
    route_base = 'appointments'

    def __init__(self):
        self.ac = AppointmentsController()
        self.wcc = WritingCenterController()
        self.mcc = MessageCenterController()
        self.wsapi = WSAPIController()

    @route('schedule')
    def schedule_appointment_landing(self):
        self.wcc.check_roles_and_route(['Student', 'Administrator'])
        return render_template('appointments/schedule_appointment.html', **locals())

    @route('view-all-appointments')
    def view_appointments(self):
        self.wcc.check_roles_and_route(['Observer', 'Administrator'])
        return render_template('appointments/view_appointments.html', **locals())

    @route('load-appointment-data', methods=['POST'])
    def load_appointment_data(self):
        self.wcc.check_roles_and_route(['Student', 'Tutor', 'Observer', 'Administrator'])
        appt_id = json.loads(request.data).get('id')
        schedule = json.loads(request.data).get('schedule')
        cancel = json.loads(request.data).get('cancel')
        pickup_sub_delete = json.loads(request.data).get('subDelete')
        tutor_edit = json.loads(request.data).get('tutorEdit')
        add_google_calendar = json.loads(request.data).get('gcalAdd', None)
        if 'Tutor' not in flask_session['USER-ROLES']:
            tutor_edit = False
        appointment = self.ac.get_appointment_by_id(appt_id)
        walk_in_hours = True if appointment.dropIn == 1 else False
        student = self.ac.get_user_by_id(appointment.student_id)
        student_name = 'None'
        if student:
            student_name = '{0} {1}'.format(student.firstName, student.lastName)
        tutor = self.ac.get_user_by_id(appointment.tutor_id)
        tutor_name = 'None'
        if tutor:
            tutor_name = '{0} {1}'.format(tutor.firstName, tutor.lastName)
        courses = self.wsapi.get_student_courses(flask_session['USERNAME'])

        return render_template('macros/appointment_modal.html', **locals())

    @route('load-appointments', methods=['POST'])
    def load_appointments(self):
        self.wcc.check_roles_and_route(['Student', 'Observer', 'Administrator'])
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
            open_no_show_appts = self.ac.get_no_show_appointments_in_range(start, end, time_limit)
            range_appointments.extend(open_no_show_appts)
        else:
            range_appointments = self.ac.get_appointments_in_range(start, end)
            walk_in_appointments = self.ac.get_walk_in_appointments_in_range(start, end)
            range_appointments.extend(walk_in_appointments)
        appointments = []
        # Formats the times to match the fullcalendar desired format
        if range_appointments:
            for appointment in range_appointments:
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
                elif appointment.scheduledStart and appointment.scheduledEnd:
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
                else:
                    start_time = None
                    end_time = None
                tutor = self.ac.get_user_by_id(appointment.tutor_id)
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

    def appointments_and_walk_ins(self):
        self.wcc.check_roles_and_route(['Tutor', 'Administrator'])
        tutor = flask_session['USERNAME']
        appointments = self.ac.get_scheduled_appointments(tutor)
        in_progress_appointments = self.ac.get_in_progress_appointments(tutor)
        in_progress_walk_ins = self.ac.get_in_progress_walk_ins(tutor)
        appointments.extend(in_progress_appointments)
        appointments.extend(in_progress_walk_ins)
        users = {}
        for appt in appointments:
            user = self.ac.get_user_by_id(appt.student_id)
            if user != None:
                name = '{0} {1}'.format(user.firstName, user.lastName)
            else:
                name = ""
            users.update({appt.student_id: name})
        return render_template('appointments/appointments_and_walk_ins.html', **locals())

    @route('/begin-checks', methods=['POST'])
    def begin_walk_in_checks(self):
        self.wcc.check_roles_and_route(['Tutor', 'Administrator'])
        username = str(json.loads(request.data).get('username'))
        if not self.wsapi.get_names_from_username(username):
            self.wcc.set_alert('danger', 'Username ' + username + ' is not valid. Please try again with a valid username.')
            return 'invalid username'
        exists = self.ac.check_for_existing_user(username)
        if exists:
            self.ac.reactivate_user(exists.id)
        else:
            name = self.wsapi.get_names_from_username(username)
            self.ac.create_user(username, name)

        courses = self.wsapi.get_student_courses(username)
        return render_template('appointments/appointment_sign_in.html', **locals())

    @route('begin-walk-in', methods=['POST'])
    def begin_walk_in(self):
        self.wcc.check_roles_and_route(['Tutor', 'Administrator'])

        form = request.form
        username = form.get('username')
        course = form.get('course')
        assignment = form.get('assignment')
        multilingual = int(form.get('multi'))
        if 'no-course' == course:
            course = None
        else:
            student_courses = self.wsapi.get_student_courses(username)
            for key in student_courses:
                if student_courses[key]['crn'] == course:
                    course_code = '{0}{1}'.format(student_courses[key]['subject'], student_courses[key]['cNumber'])
                    instructor_email = '{0}@bethel.edu'.format(student_courses[key]['instructorUsername'])
                    course = {
                        'course_code': course_code,
                        'section': student_courses[key]['section'],
                        'instructor': student_courses[key]['instructor'],
                        'instructor_email': instructor_email
                    }
                    break
        user = self.ac.get_user_by_username(username)
        tutor = self.ac.get_user_by_username(flask_session['USERNAME'])
        appt = self.ac.begin_walk_in_appointment(user, tutor, course, assignment, multilingual)
        if not appt:
            self.wcc.set_alert('danger', 'Walk in appointment failed to be started.')
            return self.appointments_and_walk_ins()
        self.wcc.set_alert('success', 'Appointment for ' + user.firstName + ' ' + user.lastName + ' started.')
        return redirect(url_for('AppointmentsView:in_progress_appointment', appt_id=appt.id))

    @route('search-appointments')
    def search_appointments(self):
        self.wcc.check_roles_and_route(['Observer', 'Administrator'])
        students = self.ac.get_users_by_role("Student")
        tutors = self.ac.get_users_by_role("Tutor")
        profs = self.ac.get_profs()
        courses = self.ac.get_courses()
        return render_template('appointments/search_appointments.html', **locals())

    @route('view-appointments')
    def student_view_appointments(self):
        self.wcc.check_roles_and_route(['Student', 'Administrator'])
        return render_template('appointments/student_view_appointments.html', **locals())

    @route('get-appointments', methods=['GET'])
    def get_users_appointments(self):
        self.wcc.check_roles_and_route(['Student', 'Administrator'])

        if flask_session['USERNAME'] in ['Student', 'Tutor', 'Administrator', 'Observer']:
            return ''

        appts = self.ac.get_all_user_appointments(flask_session['USERNAME'])
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
            elif appointment.scheduledStart and appointment.scheduledEnd:
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
            else:
                start_time = None
                end_time = None
            tutor = self.ac.get_user_by_id(appointment.tutor_id)
            appointments.append({
                'id': appointment.id,
                'studentId': appointment.student_id,
                'tutorName': '{0} {1}'.format(tutor.firstName, tutor.lastName),
                'startTime': start_time,
                'endTime': end_time,
                'multilingual': appointment.multilingual,
                'dropIn': appointment.dropIn
            })

        return jsonify(appointments)

    @route('schedule-appointment', methods=['POST'])
    def schedule_appointment(self):
        self.wcc.check_roles_and_route(['Student', 'Administrator'])
        appt_id = str(json.loads(request.data).get('appt_id'))
        course = str(json.loads(request.data).get('course'))
        assignment = str(json.loads(request.data).get('assignment'))
        username = flask_session['USERNAME']
        if username in ['Administrator', 'Observer', 'Tutor', 'Student']:
            self.wcc.set_alert('danger', 'You cannot schedule an appointment while acting as a role.')
        else:
            # Checks if the user already exists in WC DB. If a user does, we either continue or reactivate them. If they
            # don't exist then we create them
            exists = self.ac.check_for_existing_user(username)
            if not exists:
                name = self.wsapi.get_names_from_username(username)
                self.ac.create_user(username, name)
            user = self.ac.get_user_by_username(username)
            # Checks to make sure the user isn't banned.
            if not user.bannedDate:
                # Checks to make sure the user is part of CAS.
                roles = self.wsapi.get_roles_for_username(username)
                cas = False
                for role in roles:
                    if 'STUDENT-CAS' == roles[role]['userRole']:
                        cas = True
                if cas:
                    appt = self.ac.get_appointment_by_id(appt_id)
                    # Checks to make sure the student hasn't scheduled the limit of appointments per week.
                    appt_limit = int(self.ac.get_appointment_limit()[0])
                    date = appt.scheduledStart
                    weekly_appts = self.ac.get_weekly_users_appointments(user.id, date)
                    if len(weekly_appts) < appt_limit:
                        # Checks to make sure the student isn't scheduled for an appointment that overlaps with the one they
                        # are trying to schedule.
                        already_scheduled = False
                        user_appointments = self.ac.get_future_user_appointments(user.id)
                        for appointment in user_appointments:
                            if appointment.scheduledStart <= appt.scheduledStart < appointment.scheduledEnd or \
                                    appointment.scheduledStart < appt.scheduledEnd <= appointment.scheduledEnd:
                                already_scheduled = True
                        if already_scheduled:
                            self.wcc.set_alert('danger', 'Failed to schedule appointment! You already have an appointment '
                                                         'that overlaps with the one you are trying to schedule.')
                        else:
                            # Sets course to none if no specific course was selected for the appointment.
                            if 'no-course' == course:
                                course = None
                            else:
                                # Gets information about the selected course for the appointment.
                                student_courses = self.wsapi.get_student_courses(username)
                                for key in student_courses:
                                    if student_courses[key]['crn'] == course:
                                        course_code = '{0}{1}'.format(student_courses[key]['subject'],
                                                                      student_courses[key]['cNumber'])
                                        instructor_email = '{0}@bethel.edu'.format(student_courses[key]['instructorUsername'])
                                        course = {
                                            'course_code': course_code,
                                            'section': student_courses[key]['section'],
                                            'instructor': student_courses[key]['instructor'],
                                            'instructor_email': instructor_email
                                        }
                                        break
                            # Schedules the appointment and sends an email to the student and tutor if it is scheduled
                            # successfully.
                            if not self.ac.get_appointment_by_id(appt_id).student_id:
                                appt = self.ac.schedule_appointment(appt_id, course, assignment)
                                if appt:
                                    self.mcc.appointment_signup_student(appt_id)
                                    self.mcc.appointment_signup_tutor(appt_id)
                                    self.wcc.set_alert('success', 'Your Appointment Has Been Scheduled! To View Your '
                                                                  'Appointments, Go To The "View Your Appointments" Page!')
                                else:
                                    self.wcc.set_alert('danger', 'Error! Appointment Not Scheduled!')
                            else:
                                self.wcc.set_alert('danger', 'Appointment has already been scheduled by someone else. Please try again.')
                    else:
                        self.wcc.set_alert('danger', 'Failed to schedule appointment. You already have ' + str(appt_limit) +
                                           ' appointments scheduled and can\'t schedule any more.')
                else:
                    # TODO MAYBE GIVE THEM A SPECIFIC EMAIL TO EMAIL?
                    self.wcc.set_alert('danger', 'Appointment NOT scheduled! Only CAS students can schedule'
                                                 ' appointments here. If you wish to schedule an appointment email a'
                                                 ' Writing Center Administrator.')
            else:
                # TODO MAYBE GIVE THEM A SPECIFIC EMAIL TO EMAIL?
                self.wcc.set_alert('danger', 'You are banned from making appointments! If you have any questions email a'
                                             ' Writing Center Administrator.')
        # Returns the appointment id to remove it from the scheduling calendar.
        return appt_id

    @route('cancel-appointment', methods=['POST'])
    def cancel_appointment(self):
        self.wcc.check_roles_and_route(['Student', 'Administrator'])
        appt_id = str(json.loads(request.data).get('appt_id'))
        cancelled = self.ac.cancel_appointment(appt_id)
        if cancelled:
            self.mcc.cancel_appointment_student(appt_id)
            self.wcc.set_alert('success', 'Successfully cancelled appointment.')
        else:
            self.wcc.set_alert('danger', 'Failed to cancel appointment.')
        return appt_id

    @route('start-appt/<int:appt_id>')
    def start_appointment(self, appt_id):
        try:
            self.ac.start_appointment(appt_id)
            self.wcc.set_alert('success', 'Appointment Started Successfully!')
            return redirect(url_for('AppointmentsView:in_progress_appointment', appt_id=appt_id))
        except Exception as error:
            self.wcc.set_alert('danger', 'Failed to start appointment: {0}.'.format(error))
            return redirect(url_for('AppointmentsView:appointments_and_walk_ins'))

    @route('toggle-no-show/<int:appt_id>')
    def toggle_no_show(self, appt_id):
        try:
            appt = self.ac.get_appointment_by_id(appt_id)
            student = self.ac.get_user_by_id(appt.student_id)
            if appt.noShow == 0:
                self.ac.mark_no_show(appt_id)
                self.ac.ban_if_no_show_check(appt.student_id)
                self.wcc.set_alert('success', '{0} {1} successfully marked as no show.'.format(student.firstName, student.lastName))
            else:
                self.ac.revert_no_show(appt_id)
                self.wcc.set_alert('success', '{0} {1} no longer marked as no show.'.format(student.firstName, student.lastName))
        except Exception as error:
            self.wcc.set_alert('danger', 'Failed to toggle no show: {0}.'.format(error))
        return redirect(url_for('AppointmentsView:appointments_and_walk_ins'))

    @route('toggle-multilingual/<int:appt_id>')
    def toggle_multilingual(self, appt_id):
        try:
            appt = self.ac.get_appointment_by_id(appt_id)
            student = self.ac.get_user_by_id(appt.student_id)
            if appt.multilingual == 0:
                self.ac.mark_multilingual(appt_id)
                self.wcc.set_alert('success', '{0} {1}\'s appointment successfully marked as multilingual.'.format(student.firstName, student.lastName))
            else:
                self.ac.revert_multilingual(appt_id)
                self.wcc.set_alert('success', '{0} {1}\'s appointment no longer marked as multilingual.'.format(student.firstName, student.lastName))
        except Exception as error:
            self.wcc.set_alert('danger', 'Failed to toggle multilingual: {0}.'.format(error))
        return redirect(url_for('AppointmentsView:appointments_and_walk_ins'))

    @route('end-appt/<int:appt_id>', methods=['post', 'get'])
    def end_appointment(self, appt_id):
        form = request.form
        course = form.get('course')
        assignment = form.get('assignment')
        notes = form.get('notes')
        suggestions = form.get('suggestions')
        ferpa_agreement = True if form.get('ferpa') == 'on' else False
        if 'no-course' == course:
            course = None
        else:
            appt = self.ac.get_appointment_by_id(appt_id)
            student = self.ac.get_user_by_id(appt.student_id)
            student_courses = self.wsapi.get_student_courses(student.username)
            for key in student_courses:
                if student_courses[key]['crn'] == course:
                    course_code = '{0}{1}'.format(student_courses[key]['subject'], student_courses[key]['cNumber'])
                    instructor_email = '{0}@bethel.edu'.format(student_courses[key]['instructorUsername'])
                    course = {
                        'course_code': course_code,
                        'section': student_courses[key]['section'],
                        'instructor': student_courses[key]['instructor'],
                        'instructor_email': instructor_email
                    }
                    break

        try:
            self.ac.end_appointment(appt_id, course, assignment, notes, suggestions)
            self.mcc.close_session_student(appt_id)
            if ferpa_agreement:
                self.mcc.end_appt_prof(appt_id)
            qualtrics_link = self.ac.get_survey_link()[0]
            self.wcc.set_alert('success', 'Appointment ended successfully!')
            return render_template('appointments/end_appointment.html', **locals())
        except Exception as error:
            self.wcc.set_alert('danger', 'Failed to end appointment: {0}.'.format(error))
            return redirect(url_for('AppointmentsView:in_progress_appointment', appt_id=appt_id))

    @route('in-progress/<int:appt_id>')
    def in_progress_appointment(self, appt_id):
        appt = self.ac.get_appointment_by_id(appt_id)
        student = self.ac.get_user_by_id(appt.student_id)
        courses = self.wsapi.get_student_courses(student.username)
        return render_template('appointments/in_progress_appointment.html', **locals())

    @route('save-changes', methods=['POST'])
    def save_changes(self):
        self.wcc.check_roles_and_route(['Tutor'])
        appt_id = json.loads(request.data).get('appt_id')
        assignment = str(json.loads(request.data).get('assignment'))
        notes = str(json.loads(request.data).get('notes'))
        suggestions = str(json.loads(request.data).get('suggestions'))
        success = self.ac.tutor_change_appt(appt_id, assignment, notes, suggestions)
        if success:
            return 'close'
        else:
            return 'failed'

    @route('/search', methods=['POST'])
    def search(self):
        self.wcc.check_roles_and_route(['Observer', 'Administrator'])
        form = request.form
        student = None if form.get('student') == 'None' else int(form.get('student'))
        tutor = None if form.get('tutor') == 'None' else int(form.get('tutor'))
        prof = None if form.get('prof') == 'None' else form.get('prof')
        course = None if form.get('course') == 'None' else form.get('course')
        start = form.get('start')
        start_date = None if start == '' else datetime.strptime(start, "%a %b %d %Y")
        end = form.get('end')
        end_date = None if end == '' else datetime.strptime(end, "%a %b %d %Y")
        # If no parameters sent in return the following message
        if student is None and tutor is None and prof is None and course is None and start_date is None and end_date is None:
            return 'Please enter parameters to search by.'
        appointments = self.ac.search_appointments(student, tutor, prof, course, start_date, end_date)
        appts_and_info = {}
        for appt in appointments:
            appts_and_info[appt] = {
                'student': self.ac.get_user_by_id(appt.student_id),
                'tutor': self.ac.get_user_by_id(appt.tutor_id)
            }
        return render_template('appointments/appointment_search_table.html', **locals())

    @route('/edit/<int:appt_id>', methods=['GET', 'POST'])
    def edit(self, appt_id):
        self.wcc.check_roles_and_route(['Administrator'])
        appt = self.ac.get_appointment_by_id(appt_id)
        all_tutors = self.ac.get_users_by_role('Tutor')
        all_students = self.ac.get_all_users()
        all_profs = self.ac.get_profs_and_emails()
        all_courses = self.ac.get_courses()
        return render_template('appointments/edit_appointment.html', **locals())

    @route('/submit-edits', methods=['POST'])
    def submit_edits(self):
        self.wcc.check_roles_and_route(['Administrator'])
        form = request.form

        appt_id = int(form.get('id'))
        tutor_id = None if form.get('tutor') == '-1' else int(form.get('tutor'))
        student_id = None if form.get('student') == '-1' else int(form.get('student'))

        date = None if form.get('date') == '' else form.get('date')
        sched_start_time = None if form.get('sched-start') == '' else form.get('sched-start')
        sched_end_time = None if form.get('sched-end') == '' else form.get('sched-end')
        if not date:
            self.wcc.set_alert('danger', 'You must select a date.')
            return redirect(url_for('AppointmentsView:edit', appt_id=appt_id))
        if sched_start_time and sched_end_time:
            sched_start_time = "{0} {1}".format(datetime.strptime(date, '%a %b %d %Y').strftime("%Y-%m-%d"), sched_start_time)
            sched_end_time = "{0} {1}".format(datetime.strptime(date, '%a %b %d %Y').strftime("%Y-%m-%d"), sched_end_time)

        actual_start_time = None if form.get('actual-start') == '' else form.get('actual-start')
        actual_end_time = None if form.get('actual-end') == '' else form.get('actual-end')
        actual_start = None if not actual_start_time else "{0} {1}".format(datetime.strptime(date, '%a %b %d %Y').strftime("%Y-%m-%d"), actual_start_time)
        actual_end = None if not actual_end_time else "{0} {1}".format(datetime.strptime(date, '%a %b %d %Y').strftime("%Y-%m-%d"), actual_end_time)

        prof = None if form.get('prof') == 'None' else form.get('prof')
        prof_email = None if form.get('email') == 'None' else form.get('email')
        course = None if form.get('course') == 'None' else form.get('course')
        section = None if form.get('section') == 'None' else int(form.get('section'))
        assignment = None if form.get('assignment') == 'None' else form.get('assignment')
        notes = None if form.get('notes') == 'None' else form.get('notes')
        suggestions = None if form.get('suggestions') == 'None' else form.get('suggestions')
        sub = int(form.get('sub-req'))
        drop_in = int(form.get('drop-in-check'))
        multilingual = int(form.get('multi-check'))
        no_show = int(form.get('no-show-check'))
        in_progress = int(form.get('in-progress-check'))

        try:
            self.ac.edit_appt(appt_id, student_id, tutor_id, sched_start_time, sched_end_time, actual_start, actual_end, prof,
                              prof_email, drop_in, sub, assignment, notes, suggestions, multilingual, course, section,
                              no_show, in_progress)
            self.wcc.set_alert('success', 'Appointment edited successfully!')
        except Exception as e:
            self.wcc.set_alert('danger', 'Failed to edit appointment: {0}.'.format(str(e)))
        return redirect(url_for('AppointmentsView:edit', appt_id=appt_id))
