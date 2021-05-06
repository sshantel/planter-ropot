from scraper_bot import *
import unittest
import requests
import csv


class TestPlanterRopot(unittest.TestCase):
    def test_handlers(self):
        """Check if Craigslist, Twilio, Slack are OK status"""
        api_handle_code = scraper_bot.craigslist_handler()
        self.assertEqual(api_handle_code, 0)
        api_handle_code = scraper_bot.slack_handler()
        self.assertEqual(api_handle_code, 0)
        api_handle_code = scraper_bot.twilio_handler()
        self.assertEqual(api_handle_code, 0)

    def test_csv(self):
        """Check if CSV is CSV object"""
        with open("listings.csv", "r") as csvfile:
            csv_reader = csv.reader(csvfile)
            next(csv_reader, None)
        self.assertTrue(str(type(csv_reader)), "_csv.reader")

    def test_lastscrape(self):
        """Scraping only dates listed after the last_scrape using Mock Listings CSV"""
        mock_csv = scraper_bot.mock_scrape()
        self.assertEqual(mock_csv, [["2021-05-04 23:56:00"], ["2021-05-03 18:22:00"]])


if __name__ == "__main__":
    unittest.main()
