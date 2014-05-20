# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
import os.path
import json
import datetime
import unittest

from presence_analyzer import main, utils


TEST_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_data.csv'
)

TEST_USERS_XML = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'sample_users.xml'
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
        self.assertEqual(resp.status_code, 200)

    def test_presence_mean_time_weekday(self):
        """
        Test presence mean time page
        """
        resp = self.client.get('/mean_time_weekday.html')
        self.assertEqual(resp.status_code, 200)

    def test_presence_start_end(self):
        """
        Test presence start-end page
        """
        resp = self.client.get('/presence_start_end.html')
        self.assertEqual(resp.status_code, 200)

    def test_api_users(self):
        """
        Test users listing.
        """
        resp = self.client.get('/api/v1/users')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 8)
        self.assertDictEqual(data[0], {u'user_id': 141, u'name': u'Adam P.'})


class PresenceAnalyzerUtilsTestCase(unittest.TestCase):
    """
    Utility functions tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})
        main.app.config.update({'USERS_XML': TEST_USERS_XML})

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

    def test_group_start_end_by_weekday(self):
        """
        Test grouping start and end time by weekday
        """
        expected_result = {
            0: {
                'starts': [], 'ends': []
            },
            1: {
                'starts': [34745], 'ends': [64792]
            },
            2: {
                'starts': [33592], 'ends': [58057]
            },
            3: {
                'starts': [38926], 'ends': [62631]
            },
            4: {
                'starts': [], 'ends': []
            },
            5: {
                'starts': [], 'ends': []
            },
            6: {
                'starts': [], 'ends': []
            }
        }
        data = utils.get_data()
        sample_data = utils.group_start_end_by_weekday(data[10])
        self.assertIsInstance(sample_data, dict)
        self.assertEqual(len(sample_data), 7)
        self.assertEqual(sample_data, expected_result)

    def test_parse_users_xml(self):
        """
        Test xml parser
        """
        parsed_data = utils.parse_users_xml()
        expected_result = {'user_id': 19, 'name': 'Anna K.'}
        self.assertEqual(len(parsed_data), 8)
        self.assertIsInstance(parsed_data, list)
        self.assertEqual(parsed_data[5], expected_result)


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
