# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
import os.path
import json
import datetime
import unittest

from presence_analyzer import main, views, utils


TEST_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_data.csv'
)


# pylint: disable=E1103
class PresenceAnalyzerViewsTestCase(unittest.TestCase):
    """
    Views tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})
        self.client = main.app.test_client()

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_mainpage(self):
        """
        Test main page redirect.
        """
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 302)
        assert resp.headers['Location'].endswith('/presence_weekday.html')

    def test_api_users(self):
        """
        Test users listing.
        """
        resp = self.client.get('/api/v1/users')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 2)
        self.assertDictEqual(data[0], {u'user_id': 10, u'name': u'User 10'})

    def test_mean_time_weekday(self):
        """
        Test users mean presence time by weekday
        """
        resp = self.client.get('/api/v1/mean_time_weekday/100')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 0)

    def test_presence_weekday(self):
        """
        Test users total presence time by weekday
        """
        resp = self.client.get('/api/v1/presence_weekday/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 8)
        self.assertListEqual(data[0], ["Weekday", "Presence (s)"])


class PresenceAnalyzerUtilsTestCase(unittest.TestCase):
    """
    Utility functions tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_get_data(self):
        """
        Test parsing of CSV file.
        """
        data = utils.get_data()
        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [10, 11])
        sample_date = datetime.date(2013, 9, 10)
        self.assertIn(sample_date, data[10])
        self.assertItemsEqual(data[10][sample_date].keys(), ['start', 'end'])
        self.assertEqual(data[10][sample_date]['start'],
                         datetime.time(9, 39, 5))

    def test_mean(self):
        """
        Test calculating arithmetic mean
        """
        self.assertIsInstance(utils.mean([1, 2, 3]), float)
        self.assertEqual(utils.mean([1, 2, 3]), 2)
        self.assertEqual(utils.mean([-10, 10]), 0)

    def test_seconds_since_midnight(self):
        """
        Test calculating amount on seconds since midnight
        """
        self.assertIsInstance(utils.seconds_since_midnight(
            datetime.datetime.now()), int)
        self.assertEqual(
            utils.seconds_since_midnight(datetime.time(2, 30, 15)), 9015)

    def test_interval(self):
        """
        Test calculating interval between two datetime.time objects in seconds
        """
        start = datetime.datetime.now()
        end = datetime.datetime.now() + datetime.timedelta(hours=1)
        self.assertIsInstance(utils.interval(start, end), int)
        self.assertEqual(utils.interval(start, end), 3600)

    def test_group_by_weekday(self):
        """
        Test groups presence entris by weekday
        """
        sample_data = utils.get_data()
        grouped_sample = utils.group_by_weekday(sample_data[10])
        expected_result_for_empty_dict = {i: [] for i in range(7)}
        expected_result_for_grouped_sample = {
            0: [],
            1: [30047],
            2: [24465],
            3: [23705],
            4: [],
            5: [],
            6: []
        }
        self.assertEqual(len(grouped_sample), 7)
        self.assertIsInstance(grouped_sample, dict)        
        self.assertEqual(
            utils.group_by_weekday({}), expected_result_for_empty_dict)
        self.assertEqual(grouped_sample, expected_result_for_grouped_sample)


def suite():
    """
    Default test suite.
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PresenceAnalyzerViewsTestCase))
    suite.addTest(unittest.makeSuite(PresenceAnalyzerUtilsTestCase))
    return suite


if __name__ == '__main__':
    unittest.main()
