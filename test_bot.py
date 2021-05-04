from scraper_bot import *
import scraper_bot as scraper_bot
import unittest
import requests


class TestSlackBot(unittest.TestCase):
    def test_slack_api_success(self):
        """Check is Slack API is responsive"""
        slack_url = "https://slack.com/api/api.test"
        response = requests.get(slack_url)
        result = response.status_code
        """OK"""
        self.assertEqual(self.test_slack_api_success(), "200")
        """Created"""
        self.assertNotEquals(self.test_slack_api_success(), "201")
        """Accepted"""
        self.assertNotEquals(self.test_slack_api_success(), "202")
        """No content"""
        self.assertNotEquals(self.test_slack_api_success(), "204")
        return result

    def test_slack_api_client_error(self):
        """Check if Slack API is a Client Error"""
        slack_url = "https://slack.com/api/api.test"
        response = requests.get(slack_url)
        result = response.status_code
        """Bad Request"""
        self.assertNotEquals(self.test_slack_api_client_error(), "400")
        """Unauthorized"""
        self.assertNotEquals(self.test_slack_api_client_error(), "401")
        """Forbidden"""
        self.assertNotEquals(self.test_slack_api_client_error(), "403")
        """Not Found"""
        self.assertNotEquals(self.test_slack_api_client_error(), "404")
        """Too Many Requests"""
        self.assertNotEquals(self.test_slack_api_client_error(), "429")
        return result

    # def test_lastscrape(self):
    #     """To only scrape new listings (that are dated after the "last scrape")"""
    #     print(scraper_bot.craigslist_soup)
    #     self.assertEqual(
    #         scraper_bot.craigslist_soup(
    #             "denver",
    #             "camry",
    #             "2021-05-01 10:00",
    #         )
    #     )


if __name__ == "__main__":
    unittest.main()
