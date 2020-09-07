import requests

import os

import slack
from slack import WebClient

from bs4 import BeautifulSoup as b_s

import csv

import sqlite3


conn = sqlite3.connect("listings.db")
cursor = conn.cursor()
c = conn.cursor()
print(c)

c.execute(
    """CREATE TABLE listings
             (id INTEGER UNIQUE,
             created TEXT,
             name TEXT,
             price TEXT,
             location TEXT NOT NULL,
             url TEXT NOT NULL UNIQUE)"""
)

# SLACK_TOKEN = os.environ["SLACK_API_TOKEN"]
SLACK_TOKEN = "xoxb-336675185190-1301453306821-3C1NASWqLNP25aIuf84se8Z7"
SLACK_CHANNEL = "#planter"


def craigslist_soup(region, term, parser):
    url = "https://{region}.craigslist.org/search/sss?query={term}".format(
        region=region, term=term
    )
    print(url)

    response = requests.get(url=url)
    soup = b_s(response.content, parser)

    return soup


c_l = craigslist_soup(region="sfbay", term="planter", parser="html.parser")


def search_query(craigslist_soup):
    posts = c_l.find_all("li", class_="result-row")
    first_cl_result = posts
    links = []
    posting_body = []
    with open("listings.csv", "w", newline="") as csvfile:
        csv_headers = ["id", "created", "name", "price", "location", "url"]
        writer = csv.DictWriter(csvfile, fieldnames=csv_headers)
        writer.writeheader()
    for post in posts:
        title_class = post.find("a", class_="result-title hdrlnk")
        links.append(title_class["href"])
        for link in links:
            response_link = requests.get(url=link)
            link_soup = b_s(response_link.content, "html.parser")
            section_body_class = link_soup.find("section", id="postingbody")
            section_body_class_text = section_body_class.text
            item_description = "".join(section_body_class_text)
            stripped = item_description.replace("\n\nQR Code Link to This Post\n", "")
            final_strip = stripped.replace("\n\n", "")
            final_final_strip = final_strip.rstrip()
            posting_body.append(final_final_strip)
            final_posting_body = "".join(posting_body)
        result_price = post.find("span", class_="result-price")
        price_test = post.a
        time_class = post.find("time", class_="result-date")
        datetime = time_class["datetime"]
        title_class = post.find("a", class_="result-title hdrlnk")
        url = title_class["href"]
        cl_id = title_class["data-id"]
        title_text = title_class.text
        neighborhood = post.find("span", class_="result-hood")
        if neighborhood is not None:
            neighborhood_text = neighborhood.text
        else:
            neighborhood_text == "No neighborhood provided"
        for price in result_price:
            cursor.execute(
                "INSERT into listings VALUES(?,?,?,?,?,?)",
                (cl_id, datetime, title_text, price, neighborhood_text, url,),
            )

            conn.commit()

        with open("listings.csv", "a") as csvfile:
            fieldnames = [
                "id",
                "created",
                "name",
                "price",
                "location",
                "url",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            for price in result_price:
                writer.writerow(
                    {
                        "id": cl_id,
                        "created": datetime,
                        "name": title_text,
                        "price": price,
                        "location": neighborhood_text,
                        "url": url,
                    }
                )
            csvfile.close()

        client = WebClient(SLACK_TOKEN)
        desc = f" {result_price.text} | {title_text} | {datetime} | {url} | {neighborhood_text} | {final_final_strip}"
        response = client.chat_postMessage(channel=SLACK_CHANNEL, text=desc,)


search_query(craigslist_soup)

