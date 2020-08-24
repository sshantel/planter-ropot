import requests
import os

from slack import WebClient
from bs4 import BeautifulSoup as b_s

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean
from sqlalchemy.orm import sessionmaker

import csv

import sqlite3

conn = sqlite3.connect("poops.db")
cursor = conn.cursor()
c = conn.cursor()
print(c)

c.execute(
    """CREATE TABLE poops
             (id integer, created text, name text, price text, location text, url text)"""
)

SLACK_TOKEN = os.environ["SLACK_API_TOKEN"]
SLACK_CHANNEL = "#planter"


def craigslist_soup(region, term, parser):
    url = f"https://{region}.craigslist.org/search/sss?query={term}"
    print(url)

    response = requests.get(url=url)
    # print(response)
    soup = b_s(response.content, parser)
    # print(soup)

    return soup


c_l = craigslist_soup(region="sfbay", term="planter", parser="html.parser")


def search_query(craigslist_soup):
    posts = c_l.find_all("li", class_="result-row")
    first_cl_result = posts
    # print(first_cl_result)
    links = []
    posting_body = []
    with open("listings.csv", "w", newline="") as csvfile:
        csv_headers = ["id", "created", "name", "price", "location", "url"]
        writer = csv.DictWriter(csvfile, fieldnames=csv_headers)
        writer.writeheader()
    for post in posts:
        title_class = post.find("a", class_="result-title hdrlnk")
        # print(f"title class is {title_class}")
        # print(title_class['href'])
        links.append(title_class["href"])
        # print(links)
        for link in links:
            # print(link)
            # print(f"link is {link}")
            response_link = requests.get(url=link)
            link_soup = b_s(response_link.content, "html.parser")
            # print(f"this is link soup {link_soup}")
            section_body_class = link_soup.find("section", id="postingbody")
            # print(f"section body class is {section_body_class}")
            # print(f"section body class text is {section_body_class.text}")
            poopoo = section_body_class.text
            item_description = "".join(poopoo)
            # .text
            # print(f"item description is {item_description}")
            stripped = item_description.replace("\n\nQR Code Link to This Post\n", "")
            # print(f"stripped is {stripped}")
            final_strip = stripped.replace("\n\n", "")
            # print(f"final strip is {final_strip}")
            final_final_strip = final_strip.rstrip()
            # print(f"final final strip is{final_final_strip}")
            # posting_body.append(section_body_class.text)
            posting_body.append(final_final_strip)
            poop = "".join(posting_body)
            # print(poop)
        result_price = post.find("span", class_="result-price")
        # print(result_price.text)
        price_test = post.a
        # print(price_test)
        time_class = post.find("time", class_="result-date")
        datetime = time_class["datetime"]
        # print(datetime)
        title_class = post.find("a", class_="result-title hdrlnk")
        url = title_class["href"]
        cl_id = title_class["data-id"]
        title_text = title_class.text
        # print(title_text)
        neighborhood = post.find("span", class_="result-hood")
        # print(f"this is neighborhood {neighborhood}")
        if neighborhood is not None:
            neighborhood_text = neighborhood.text
        else:
            neighborhood_text == "No neighborhood provided"
        c.execute(
            "INSERT INTO poops VALUES('poop', 'poop', 'poop', 'poop', 'poop', 'poop')"
        )
        conn.commit()

        # with open("listings.csv", "a") as csvfile:
        #     fieldnames = [
        #         "id",
        #         "created",
        #         "name",
        #         "price",
        #         "location",
        #         "url",
        #     ]
        #     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        #     # writer.writeheader()
        #     for price in result_price:
        #         writer.writerow(
        #             {
        #                 "id": cl_id,
        #                 "created": datetime,
        #                 "name": title_text,
        #                 "price": price,
        #                 "location": neighborhood_text,
        #                 "url": url,
        #             }
        #         )
        #     csvfile.close()


# engine = create_engine("sqlite:///listings.db", echo=False)
# print(engine)
# Base = declarative_base()
# print(Base)


# Base.metadata.create_all(engine)

# Session = sessionmaker(bind=engine)
# session = Session()


# class Listing(Base):

#     __tablename__ = "listings"
#     id = Column(Integer, primary_key=True)
#     created = Column(String)
#     name = Column(String)
#     price = Column(String)
#     location = Column(String)
#     url = Column(String, unique=True)


# listing = Listing(url="poop")
# for listin in listing:
#     session.add(listing)
#     session.commit()


# def post_to_slack():
#     client = WebClient(SLACK_TOKEN)
#     desc = f" {result_price.text} | {title_text} | {datetime} | {url} | {neighborhood_text} | {final_final_strip}"
#     response = client.chat_postMessage(channel=SLACK_CHANNEL, text=desc,)
#     # print(response)
# post_to_slack()

search_query(craigslist_soup)
# need functions: slackbot, calculate_distance_from


# class Contacts(Base):
#     __tablename__ = "contacts"
#     contact_id = Column(Integer, primary_key=True)
#     first_name = Column(String, nullable=False)
#     last_name = Column(String, nullable=False)
#     email = Column(String, nullable=False, unique=True)
#     phone = Column(String, nullable=False, unique=True)


# def test_add_to_db():
#     contact = Contacts(
#         first_name="poop", last_name="poop", email="poop@gmail.com", phone="900"
#     )
#     session.add(contact)
#     session.commit()


# test_add_to_db()
