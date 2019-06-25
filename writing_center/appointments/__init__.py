from flask_classy import FlaskView, route, request
from flask import render_template, jsonify, json
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
        get_name = self.ac.get_user_by_username
        return render_template('appointments/view_all_appointments.html', **locals())

    @route('/view-yearly/<int:selected_year>')
    def view_yearly_appointments(self, selected_year):
        appointments = self.ac.get_yearly_appointments(selected_year)
        get_name = self.ac.get_user_by_username
        select_year = selected_year
        return render_template('appointments/view_yearly_appointments.html', **locals())

    def appointments_and_walk_ins(self):
        return render_template('appointments/appointments_and_walk_ins.html', **locals())

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
            if appointment.ActualStartTime:
                start_time = '{0}-{1}-{2}T{3}:{4}:{5}'.format(appointment.ActualStartTime.year,
                                                              appointment.ActualStartTime.strftime('%m'),
                                                              appointment.ActualStartTime.strftime('%d'),
                                                              appointment.ActualStartTime.strftime('%I'),
                                                              appointment.ActualStartTime.strftime('%M'),
                                                              appointment.ActualStartTime.strftime('%S'))
                end_time = '{0}-{1}-{2}T{3}:{4}:{5}'.format(appointment.CompletedTime.year,
                                                            appointment.CompletedTime.strftime('%m'),
                                                            appointment.CompletedTime.strftime('%d'),
                                                            appointment.CompletedTime.strftime('%I'),
                                                            appointment.CompletedTime.strftime('%M'),
                                                            appointment.CompletedTime.strftime('%S'))
            else:
                start_time = '{0}-{1}-{2}T{3}:{4}:{5}'.format(appointment.StartTime.year,
                                                              appointment.StartTime.strftime('%m'),
                                                              appointment.StartTime.strftime('%d'),
                                                              appointment.StartTime.strftime('%I'),
                                                              appointment.StartTime.strftime('%M'),
                                                              appointment.StartTime.strftime('%S'))
                end_time = '{0}-{1}-{2}T{3}:{4}:{5}'.format(appointment.EndTime.year,
                                                            appointment.EndTime.strftime('%m'),
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

        return jsonify(appointments)

    @route('open-appointments', methods=['GET'])
    def get_open_appointments(self):
        all_open_appts = self.ac.get_all_open_appointments()
        appointments = []
        for appointment in all_open_appts:
            start_time = '{0}-{1}-{2}T{3}:{4}:{5}'.format(appointment.StartTime.year,
                                                          appointment.StartTime.strftime('%m'),
                                                          appointment.StartTime.strftime('%d'),
                                                          appointment.StartTime.strftime('%H'),
                                                          appointment.StartTime.strftime('%M'),
                                                          appointment.StartTime.strftime('%S'))
            end_time = '{0}-{1}-{2}T{3}:{4}:{5}'.format(appointment.EndTime.year,
                                                        appointment.EndTime.strftime('%m'),
                                                        appointment.EndTime.strftime('%d'),
                                                        appointment.EndTime.strftime('%H'),
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
