# -*- coding: utf-8 -*-
"""
Defines views.
"""

import calendar
from flask import render_template

from presence_analyzer.main import app
from presence_analyzer import utils
from lxml import etree
import logging
log = logging.getLogger(__name__)  # pylint: disable-msg=C0103


@app.route('/')
def mainpage():
    """
    Redirects to front page.
    """
    return render_template('presence_weekday.html')


@app.route('/<template_name>')
def presence(template_name):
    """
    Renders template to presence mean time page
    """
    return render_template(template_name)


@app.route('/api/v1/users', methods=['GET'])
@utils.jsonify
def users_view():
    """
    Users listing for dropdown.
    """
    # data = utils.get_data()
    # return [{'user_id': i, 'name': 'User {0}'.format(str(i))}
    #         for i in data.keys()]
    return utils.parse_users_xml()


@app.route('/api/v1/mean_time_weekday/', methods=['GET'])
@app.route('/api/v1/mean_time_weekday/<int:user_id>', methods=['GET'])
@utils.jsonify
def mean_time_weekday_view(user_id=None):
    """
    Returns mean presence time of given user grouped by weekday.
    """
    data = utils.get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        return []

    weekdays = utils.group_by_weekday(data[user_id])
    result = [(calendar.day_abbr[weekday], utils.mean(intervals))
              for weekday, intervals in weekdays.items()]

    return result


@app.route('/api/v1/presence_weekday/', methods=['GET'])
@app.route('/api/v1/presence_weekday/<int:user_id>', methods=['GET'])
@utils.jsonify
def presence_weekday_view(user_id=None):
    """
    Returns total presence time of given user grouped by weekday.
    """
    data = utils.get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        return []

    weekdays = utils.group_by_weekday(data[user_id])
    result = [(calendar.day_abbr[weekday], sum(intervals))
              for weekday, intervals in weekdays.items()]

    result.insert(0, ('Weekday', 'Presence (s)'))
    return result


@app.route('/api/v1/presence_start_end/', methods=['GET'])
@app.route('/api/v1/presence_start_end/<int:user_id>', methods=['GET'])
@utils.jsonify
def presence_start_end_view(user_id=None):
    """
    Return average presence time of given user
    """
    data = utils.get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        return []

    start_end_by_weekday = utils.group_start_end_by_weekday(data[user_id])

    result = [
        (
            calendar.day_abbr[weekday],
            utils.mean(intervals['starts']),
            utils.mean(intervals['ends'])
        )
        for weekday, intervals in start_end_by_weekday.items()
    ]

    return result
