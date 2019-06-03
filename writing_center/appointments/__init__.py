from flask_classy import FlaskView, route
from flask import render_template


class AppointmentsView(FlaskView):
    route_base = ''

    def __init__(self):
        pass

    @route('/center-manager/edit-appointments/view')
    def view_all_appointments(self):
        return render_template('appointments/view_all_appointments.html', **locals())

    def scheduled_appointments(self):
        return render_template('appointments/scheduled_appointments.html', **locals())
