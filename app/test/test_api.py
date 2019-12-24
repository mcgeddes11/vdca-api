import requests, os
import unittest

# These tests should be run against a local docker container as built and started using the scripts in the
# base directory.  API_KEY should be an environment variable containing a valid API key.

VALID_API_KEY = os.getenv("API_KEY", None)
if VALID_API_KEY is None:
    raise Exception("No valid API key found - did you set the API_KEY environment variable?")

# base_url = "http://107.170.241.11/{}?api_key={}&season={}&grade_id={}&finals_flag={}"
base_url = "http://localhost:80/{}?api_key={}&season={}&grade_id={}&finals_flag={}"


class TestApi(unittest.TestCase):

    def test_fielding_valid(self):
        response = requests.get(base_url.format("fieldingStats", VALID_API_KEY, 2009, 9302, 0), timeout=5)
        self.assertEqual(response.status_code,200)
        self.assertGreaterEqual(len(response.json()),0)

    def test_bowling_valid(self):
        response = requests.get(base_url.format("bowlingStats", VALID_API_KEY, 2009, 9302, 0), timeout=5)
        self.assertEqual(response.status_code,200)
        self.assertGreaterEqual(len(response.json()),0)

    def test_batting_valid(self):
        response = requests.get(base_url.format("battingStats", VALID_API_KEY, 2009, 9302, 0), timeout=5)
        self.assertEqual(response.status_code,200)
        self.assertGreaterEqual(len(response.json()),0)

    def test_year_outside_range(self):
        response = requests.get(base_url.format("bowlingStats", VALID_API_KEY, 2000, 9302, 0), timeout=5)
        self.assertEqual(response.status_code, 404)

    def test_invalid_finals_flag(self):
        response = requests.get(base_url.format("bowlingStats", VALID_API_KEY, 2000, 9302, 12), timeout=5)
        self.assertEqual(response.status_code, 404)

    def test_missing_argument(self):
        url = base_url.format("bowlingStats", VALID_API_KEY, 2000, 9302, 12)
        url = url.replace("&finals_flag=12","")
        response = requests.get(url, timeout=5)
        self.assertEqual(response.status_code, 400)

    def test_bad_method_call(self):
        response = requests.get(base_url.format("someRandomMethod", VALID_API_KEY, 2000, 9302, 12), timeout=5)
        self.assertEqual(response.status_code, 404)