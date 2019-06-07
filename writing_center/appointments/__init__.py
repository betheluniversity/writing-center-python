from flask_classy import FlaskView, route
from flask import render_template


class AppointmentsView(FlaskView):
    route_base = ''

    def __init__(self):
        pass

    @route('/center-manager/edit-appointments/view')
    def view_all_appointments(self):
        return render_template('appointments/view_all_appointments.html', **locals())

    def appointments_and_walk_ins(self):
        return render_template('appointments/appointments_and_walk_ins.html', **locals())

    def create_appointment(self):
        return render_template('appointments/create_appointment.html', **locals())

    def student_view_appointments(self):
        return render_template('appointments/student_view_appointments.html', **locals())
