# -*- coding: utf-8 -*-
"""
Defines views.
"""

import calendar, datetime
from flask import redirect

from presence_analyzer.main import app
from presence_analyzer.utils import jsonify, get_data, mean, group_by_weekday

import logging
log = logging.getLogger(__name__)  # pylint: disable-msg=C0103


@app.route('/')
def mainpage():
    """
    Redirects to front page.
    """
    return redirect('/static/presence_weekday.html')


@app.route('/api/v1/users', methods=['GET'])
@jsonify
def users_view():
    """
    Users listing for dropdown.
    """
    data = get_data()
    return [{'user_id': i, 'name': 'User {0}'.format(str(i))}
            for i in data.keys()]


@app.route('/api/v1/mean_time_weekday/<int:user_id>', methods=['GET'])
@jsonify
def mean_time_weekday_view(user_id):
    """
    Returns mean presence time of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        return []

    weekdays = group_by_weekday(data[user_id])
    result = [(calendar.day_abbr[weekday], mean(intervals))
              for weekday, intervals in weekdays.items()]

    return result


@app.route('/api/v1/presence_weekday/<int:user_id>', methods=['GET'])
@jsonify
def presence_weekday_view(user_id):
    """
    Returns total presence time of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        return[]

    weekdays = group_by_weekday(data[user_id])
    result = [(calendar.day_abbr[weekday], sum(intervals))
              for weekday, intervals in weekdays.items()]

    result.insert(0, ('Weekday', 'Presence (s)'))
    return result

@app.route('/api/v1/presence_start_end/<int:user_id>', methods=['GET'])
@jsonify
def presence_start_end(user_id):
    """
    Return average presence time of given user
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        return []

    total_start, total_end = [], []
    start_counter , end_counter= 0, 0

    for date in data[user_id]:
        total_start.append(str(data[user_id][date]['start']))
        total_end.append(str(data[user_id][date]['end']))

    total_start_sec = 0
    for tm in total_start:
        time_part = [int(s) for s in tm.split(':')]
        total_start_sec += (time_part[0] * 60 + time_part[1]) * 60 + time_part[2]
        start_counter += 1
    total_start_sec, sec = divmod(total_start_sec, 60)
    hr, min = divmod(total_start_sec, 60)
    start_sum = "%d:%02d:%02d" % (hr, min, sec)

    start_sum_hour = start_sum.split(':')[0]
    start_sum_min = start_sum.split(':')[1]
    start_sum_sec = start_sum.split(':')[2]    

    total_end_sec = 0
    for tm in total_end:
        time_part = [int(s) for s in tm.split(':')]
        total_end_sec += (time_part[0] * 60 + time_part[1]) * 60 + time_part[2]
        end_counter += 1
    total_end_sec, sec = divmod(total_end_sec, 60)
    hr, min = divmod(total_end_sec, 60)
    end_sum = "%d:%02d:%02d" % (hr, min, sec)

    end_sum_hour = end_sum.split(':')[0]
    end_sum_min = end_sum.split(':')[1]
    end_sum_sec = end_sum.split(':')[2]

    result = str(int(start_sum_hour)/start_counter) + ":" + str(int(start_sum_min)/start_counter) + ":" + str(int(start_sum_sec)/start_counter)

    return result