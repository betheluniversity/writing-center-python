from flask_classy import FlaskView, route, request
from flask import render_template, jsonify, json, redirect, url_for
from flask import session as flask_session
from datetime import datetime

from writing_center.appointments.appointments_controller import AppointmentsController
from writing_center.writing_center_controller import WritingCenterController


class AppointmentsView(FlaskView):
    route_base = 'appointments'

    def __init__(self):
        self.ac = AppointmentsController()
        self.wcc = WritingCenterController()

    def index(self):
        years = self.ac.get_years()
        return render_template('appointments/select_view.html', **locals())

    @route('/view-all')
    def view_all_appointments(self):
        appointments = self.ac.get_filled_appointments()
        appts_data = {}
        for appt in appointments:
            student_info = self.ac.get_user_info(appt.student_id)
            tutor_info = self.ac.get_user_info(appt.tutor_id)
            appts_data[appt] = {
                'student_first': student_info.firstName if student_info else None,
                'student_last': student_info.lastName if student_info else None,
                'student_username': student_info.username if student_info else None,
                'tutor_first': tutor_info.firstName if tutor_info else None,
                'tutor_last': tutor_info.lastName if tutor_info else None,
                'tutor_username': tutor_info.username if tutor_info else None
            }
        return render_template('appointments/view_all_appointments.html', **locals())

    @route('/view-yearly/<int:selected_year>')
    def view_yearly_appointments(self, selected_year):
        appointments = self.ac.get_yearly_appointments(selected_year)
        appts_data = {}
        for appt in appointments:
            student_info = self.ac.get_user_info(appt.student_id)
            tutor_info = self.ac.get_user_info(appt.tutor_id)
            if student_info:
                appts_data[appt] = {
                    'student_first': student_info.firstName,
                    'student_last': student_info.lastName,
                    'student_username': student_info.username,
                }
            if tutor_info:
                appts_data[appt].update({
                    'tutor_first': tutor_info.firstName,
                    'tutor_last': tutor_info.lastName,
                    'tutor_username': tutor_info.username
                })
        select_year = selected_year
        return render_template('appointments/view_yearly_appointments.html', **locals())

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

    @route('open-appointments', methods=['GET'])
    def get_open_appointments(self):
        all_open_appts = self.ac.get_all_open_appointments()
        appointments = []
        for appointment in all_open_appts:
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

    @route('schedule-appointment', methods=['POST'])
    def schedule_appointment(self):
        id = str(json.loads(request.data).get('id'))
        start_time = str(json.loads(request.data).get('startTime'))
        end_time = str(json.loads(request.data).get('endTime'))
        appt = self.ac.create_appointment(id, start_time, end_time)
        if appt:
            self.wcc.set_alert('success', 'Your Appointment Has Been Scheduled!')
        else:
            self.wcc.set_alert('danger', 'Error! Appointment Not Scheduled!')

        return id

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
