from flask_classy import FlaskView, route
from flask import render_template
from datetime import datetime

from writing_center.appointments.appointments_controller import AppointmentsController


class AppointmentsView(FlaskView):
    route_base = 'appointments'

    def __init__(self):
        self.ac = AppointmentsController()

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

    def student_view_appointments(self):
        return render_template('appointments/student_view_appointments.html', **locals())
