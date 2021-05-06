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

    def test_csv(self):
        """Check if listings are being written to CSV"""
        readerObject = finaImport.importCSV("toe")
        self.assertTrue(str(type(readerObject)), "_csv.reader")

    def test_lastscrape(self):
        """Scraping only dates listed after the last_scrape using Mock Listings CSV"""
        mock_csv = scraper_bot.mock_scrape()
        self.assertEqual(mock_csv, [["2021-05-04 23:56:00"], ["2021-05-03 18:22:00"]])


if __name__ == "__main__":
    unittest.main()
