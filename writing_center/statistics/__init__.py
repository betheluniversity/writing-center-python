from flask_classy import FlaskView, route
from flask import render_template, request, json
from flask import session as flask_session
from datetime import datetime, timedelta

from writing_center.statistics.statistics_controller import StatisticsController
from writing_center.writing_center_controller import WritingCenterController


class StatisticsView(FlaskView):
    def __init__(self):
        self.sc = StatisticsController()
        self.wcc = WritingCenterController()

    @route('/stats')
    def stats(self):
        self.wcc.check_roles_and_route(['Observer', 'Administrator'])
        # Use the default start and end dates to get the first tables of data
        start = flask_session['DATE-SELECTOR-START']
        end = flask_session['DATE-SELECTOR-END']
        value = flask_session['DATE-SELECTOR-VALUE']

        appointments, walk_in_appts, no_show_appts = self.get_statistics_data(start, end, value)

        return render_template('statistics/statistics.html', **locals())

    @route('/hours-worked')
    def hours_worked(self):
        self.wcc.check_roles_and_route(['Tutor', 'Administrator'])
        return render_template('statistics/hours_worked.html', **locals())

    @route('/get-hours', methods=['POST'])
    def get_hours_worked(self):
        self.wcc.check_roles_and_route(['Tutor', 'Administrator'])

        if flask_session['USERNAME'] in ['Student', 'Tutor', 'Administrator', 'Observer']:
            return "No user selected"

        start = str(json.loads(request.data).get('start'))
        end = str(json.loads(request.data).get('end'))
        start = datetime.strptime(start, '%a %b %d %Y')
        end = datetime.strptime(end, '%a %b %d %Y')
        appointments, time = self.sc.get_appt_hours(start, end, flask_session['USERNAME'])

        user = self.sc.get_user_by_username(flask_session['USERNAME'])
        start = start.strftime('%B %d %Y')
        end = end.strftime('%B %d %Y')
        return render_template('statistics/hours_worked_table.html', **locals(), id_to_user=self.sc.get_user_by_id)

    @route('/handle-stats-change', methods=['POST'])
    def handle_stats_change(self):
        self.wcc.check_roles_and_route(['Observer', 'Administrator'])
        start = str(json.loads(request.data).get('startDate'))
        end = str(json.loads(request.data).get('endDate'))
        start = datetime.strptime(start, '%a %b %d %Y')
        end = datetime.strptime(end, '%a %b %d %Y')
        value = str(json.loads(request.data).get('value'))
        stat_id = str(json.loads(request.data).get('id'))
        # We store what 'page' we are on last so check which 'page' we were last on and apply those tables to it
        if stat_id == 'busyness' or flask_session['STATISTICS-PAGE'] == 'busyness' and stat_id != 'course-busyness':

            appointments, walk_in_appts, no_show_appts, busiest_day, busiest_tod, busiest_week, busiest_tutors \
                = self.get_statistics_data(start, end, value, stat_id)
        elif stat_id == 'course-busyness' or flask_session['STATISTICS-PAGE'] == 'course-busyness':
            appointments, walk_in_appts, no_show_appts, courses = self.get_statistics_data(start, end, value, stat_id)
        else:
            # If we aren't on the busyness or course-busyness page, then we are on the homepage
            appointments, walk_in_appts, no_show_appts, = self.get_statistics_data(start, end, value, stat_id)
        # print(flask_session['DATE-SELECTOR-START'])
        return render_template('statistics/statistics_tables.html', **locals())

    def get_statistics_data(self, start, end, value, stat_id=''):
        self.wcc.check_roles_and_route(['Observer', 'Administrator'])
        # Set stored values
        flask_session['DATE-SELECTOR-START'] = start
        flask_session['DATE-SELECTOR-END'] = end
        flask_session['DATE-SELECTOR-VALUE'] = value
        # If stat_id is date-appt-change that means that either the date or type of appointment we are viewing has
        # changed so we must check which 'page' we are on by looking at what is stored in the session
        if stat_id == 'date-appt-change':
            stat_id = flask_session['STATISTICS-PAGE']
        else:
            # Else we are changing which 'page' we are saving that we are on
            flask_session['STATISTICS-PAGE'] = stat_id
        # Gets some basic appointment data
        appointments = self.sc.get_appointments(start, end, value)
        walk_in_appts = self.sc.get_walk_in_appointments(start, end, value)
        no_show_appts = self.sc.get_no_show_appointments(start, end, value)
        appts_list = []
        appts_list.extend(appointments)
        appts_list.extend(walk_in_appts)
        # If stat_id == busyness then we are only looking at busyness statistics so only return them to save time
        if stat_id == 'busyness':
            # Used to get the busiest week(s)
            busiest_week = {}
            beginning_of_week = start
            mid_week = start
            # Assume that we are starting on a Sunday
            in_mid_week = False
            # If we aren't starting on a Sunday then we are somewhere in the middle of the week
            if start.weekday() != 6:
                in_mid_week = True
            while start < end:
                # If our iterator, start, is Sunday, we can just keep moving a week forward in time to get our date
                # range
                if start.weekday() == 6:
                    # If we started in the middle of the week, than our first date range is going to be different than
                    # the rest of our date ranges so we have some custom logic for it
                    if in_mid_week:
                        in_mid_week = False
                        beginning_of_week = beginning_of_week.replace(hour=0, minute=0, second=0)
                        mid_week = mid_week.replace(hour=23, minute=59, second=59)
                        week_str = '{0} - {1}'.format(beginning_of_week.strftime('%m/%d/%Y'), mid_week.strftime('%m/%d/%Y'))
                        busiest_week.update({
                            week_str: {
                                'start': beginning_of_week,
                                'end': mid_week,
                                'count': 0
                            }
                        })
                    # Update values
                    beginning_of_week = start
                    start += timedelta(weeks=1)  # Add a week for next session
                    end_of_week = start - timedelta(days=1)
                    beginning_of_week = beginning_of_week.replace(hour=0, minute=0, second=0)
                    end_of_week = end_of_week.replace(hour=23, minute=59, second=59)
                    # If end_of_week is less than our end date, then we are still iterating through the dates so we can
                    # create our current week date range using the beginning_of_week and end_of_week variables
                    if end_of_week < end:
                        week_str = '{0} - {1}'.format(beginning_of_week.strftime('%m/%d/%Y'),
                                                      end_of_week.strftime('%m/%d/%Y'))
                        busiest_week.update({
                            week_str: {
                                'start': beginning_of_week,
                                'end': end_of_week,
                                'count': 0
                            }
                        })
                    else:
                        # If end is greater or equal to end_of_week, then we are stopping at some point midweek, so we
                        # have this custom logic to create the final week date range
                        end = end.replace(hour=23, minute=59, second=59)
                        week_str = '{0} - {1}'.format(beginning_of_week.strftime('%m/%d/%Y'), end.strftime('%m/%d/%Y'))
                        busiest_week.update({
                            week_str: {
                                'start': beginning_of_week,
                                'end': end,
                                'count': 0
                            }
                        })
                else:
                    # Moves us to the next day until we are on a Sunday
                    mid_week = start
                    # If the next day is equal to the end of the date range, then we haven't encountered a Sunday and
                    # thus we should just show our week as the first start value and the end value. Once start is
                    # updated below, we will break out of the while loop
                    if start + timedelta(days=1) == end:
                        beginning_of_week = beginning_of_week.replace(hour=0, minute=0, second=0)
                        end = end.replace(hour=23, minute=59, second=59)
                        week_str = '{0} - {1}'.format(beginning_of_week.strftime('%m/%d/%Y'), end.strftime('%m/%d/%Y'))
                        busiest_week.update({
                            week_str: {
                                'start': beginning_of_week,
                                'end': end,
                                'count': 0
                            }
                        })
                    # else we will increase the day by 1 to keep searching for a Sunday
                    start += timedelta(days=1)  # Adds a day until we are on sunday
            busiest_day = {}
            busiest_tod = {}
            busiest_tutors = {}
            for appt in appts_list:
                # Used to get the busiest day(s)
                if appt.scheduledStart and appt.scheduledEnd:
                    date = appt.scheduledStart.strftime('%b %d %Y')
                else:
                    date = appt.actualStart.strftime("%b %d %Y")
                try:
                    if busiest_day[date] != None:
                        count = busiest_day[date] + 1
                        busiest_day.update({
                            date: count
                        })
                except Exception as e:
                    busiest_day.update({
                        date: 1
                    })
                # Used to get busiest time(s) of day
                if appt.scheduledStart and appt.scheduledEnd:
                    timeslot = '{0} - {1}'.format(self.sc.datetimeformat(appt.scheduledStart),
                                                  self.sc.datetimeformat(appt.scheduledEnd))
                else:
                    timeslot = '{0} - {1} (Walk In)'.format(self.sc.datetimeformat(appt.actualStart),
                                                  self.sc.datetimeformat(appt.actualEnd))
                try:
                    if busiest_tod[timeslot] != None:
                        count = busiest_tod[timeslot] + 1
                        busiest_tod.update({
                            timeslot: count
                        })
                except Exception as e:
                    busiest_tod.update({
                        timeslot: 1
                    })
                # Used to get busiest week(s)
                for week in busiest_week:
                    if appt.scheduledStart and appt.scheduledEnd:
                        time_start = appt.scheduledStart
                        time_end = appt.scheduledEnd
                    else:
                        time_start = appt.actualStart
                        time_end = appt.actualEnd
                    if time_start > busiest_week[week]['start'] and time_end < busiest_week[week]['end']:
                        count = busiest_week[week]['count'] + 1
                        busiest_week[week].update({
                            'count': count
                        })
                # Used to get busiest tutor(s)
                tutor = self.sc.get_user_by_id(appt.tutor_id)
                tutor_str = '{0} {1} ({2})'.format(tutor.firstName, tutor.lastName, tutor.username)
                try:
                    if busiest_tutors[tutor_str] != None:
                        count = busiest_tutors[tutor_str] + 1
                        busiest_tutors.update({
                            tutor_str: count
                        })
                except Exception as e:
                    busiest_tutors.update({
                        tutor_str: 1
                    })
            return appointments, walk_in_appts, no_show_appts, busiest_day, busiest_tod, busiest_week, busiest_tutors
        elif stat_id == 'course-busyness':
            # Else if stat_id == course-busyness we are only looking at courses so only return that data
            courses = {}
            for appt in appts_list:
                # Used to get the Courses
                course_str = '{0} {1}'.format(appt.courseCode, appt.courseSection)
                try:
                    if courses[course_str] != None:
                        count = courses[course_str]['count'] + 1
                        courses[course_str].update({
                            'count': count
                        })
                except Exception as e:
                    if appt.courseCode:
                        course_code = appt.courseCode
                        tag = appt.courseCode[-1:]
                        if tag.isalpha() and tag.isupper():
                            course_code = appt.courseCode[:-1]
                            courses.update({
                                course_str: {
                                    'courseCode': course_code,
                                    'tag': tag,
                                    'section': appt.courseSection,
                                    'profName': appt.profName,
                                    'count': 1
                                }
                            })
                        else:
                            courses.update({
                                course_str: {
                                    'courseCode': course_code,
                                    'tag': '',
                                    'section': appt.courseSection,
                                    'profName': appt.profName,
                                    'count': 1
                                }
                            })
            return appointments, walk_in_appts, no_show_appts, courses
        else:
            # Else we are on the statistics homepage so only return general appointment information
            return appointments, walk_in_appts, no_show_appts
