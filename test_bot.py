# from scraper_bot import *
import scraper_bot as scraper_bot
import unittest
import requests


class TestSlackBot(unittest.TestCase):
    def test_handlers(self):
        """Check if APIs are OK status"""
        api_handle_code = scraper_bot.craigslist_handler()
        self.assertEqual(api_handle_code, 0)
        api_handle_code = scraper_bot.slack_handler()
        self.assertEqual(api_handle_code, 0)
        api_handle_code = scraper_bot.twilio_handler()
        self.assertEqual(api_handle_code, 0)

    def check_csv(self):
        """Check if listings are being written to CSV"""
        pass

    def test_lastscrape(self):
        """Test last scrape with mock CSV file"""
        mock_csv = scraper_bot.mock_scrape()
        print(mock_csv)
        pass

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
