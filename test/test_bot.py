# from scraper import *
import unittest
import requests


class TestSlackBot(unittest.TestCase):
    def test_slack_api(self):
        slack_url = "https://slack.com/api/api.test"
        response = requests.get(slack_url)
        result = response.status_code
        return result
        self.assertEqual(self.test_slack_api(), "200")

    def test_spellcheck():
        pass


if __name__ == "__main__":
    unittest.main()
