from flask_classy import FlaskView, route
from flask import render_template, request, json
from flask import session as flask_session
from datetime import datetime

from writing_center.statistics.statistics_controller import StatisticsController


class StatisticsView(FlaskView):
    def __init__(self):
        self.sc = StatisticsController()

    def index(self):
        return render_template('statistics/index.html', **locals())

    @route('/center-manager/statistics/')
    def stats(self):
        return render_template('statistics/statistics.html', **locals())

    @route('/observer/statistics/')
    def stats_observer(self):
        return render_template('statistics/statistics_observer.html', **locals())

    def view_reports(self):
        return render_template('statistics/view_reports.html', **locals())

    @route('/hours-worked')
    def hours_worked(self):
        return render_template('statistics/hours_worked.html', **locals())

    @route('/get-hours', methods=['POST'])
    def get_hours_worked(self):
        start = str(json.loads(request.data).get('start'))
        end = str(json.loads(request.data).get('end'))
        start = datetime.strptime(start, '%a %b %d %Y')
        end = datetime.strptime(end, '%a %b %d %Y')
        appointments = self.sc.get_appt_hours(start, end, flask_session['USERNAME'])
        time = 0

        for appointment in appointments:
            start_time = str(appointment.actualStart).split(' ')[1].split(':')
            start_min = int(start_time[1])
            start_hour = int(start_time[0])
            if 0 < start_min and start_min < 15:
                start_min = 15
            elif 15 < start_min and start_min < 30:
                start_min = 30
            elif 30 < start_min and start_min < 45:
                start_min = 45
            elif 45 < start_min and start_min < 60:
                start_min = 0
                if start_hour < 24:
                    start_hour += 1
            end_time = str(appointment.actualEnd).split(' ')[1].split(':')
            end_min = int(end_time[1])
            end_hour = int(end_time[0])
            if 0 < end_min and end_min < 15:
                end_min = 15
            elif 15 < end_min and end_min < 30:
                end_min = 30
            elif 30 < end_min and end_min < 45:
                end_min = 45
            elif 45 < end_min and end_min < 60:
                end_min = 0
                if end_hour < 24:
                    end_hour += 1
            time += end_hour - start_hour + ((end_min - start_min) / 60)

        user = self.sc.get_user_by_username(flask_session['USERNAME'])
        start = start.strftime('%B %d %Y')
        end = end.strftime('%B %d %Y')
        message = '<h5>{0} {1} has worked {2} hours worked between {3} and {4}</h5>'.format(user.firstName, user.lastName, time, start, end)
        return message
