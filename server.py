import requests
import os

from slack import WebClient

from bs4 import BeautifulSoup as b_s

import csv

import sqlite3

import time
from datetime import datetime

SLACK_TOKEN = os.environ["SLACK_API_TOKEN"]
SLACK_CHANNEL = "#planter_ropot"
 
def connect_to_db(name):
    conn = sqlite3.connect(name)
    c = conn.cursor()
    return (c, conn)

def create_csv():
    with open("listings.csv", "w", newline="") as csvfile:
        csv_headers = ["id", "created", "name", "price", "location", "url", "description"]
        writer = csv.DictWriter(csvfile, fieldnames=csv_headers)
        writer.writeheader()
create_csv()

def create_listings_db():
    c = connect_to_db("listings.db")
    c[0].execute(
        """CREATE TABLE IF NOT EXISTS listings
                (id INTEGER,
                created TEXT,
                name TEXT,
                price TEXT,
                location TEXT NOT NULL,
                url TEXT NOT NULL,
                description TEXT)"""
    )

create_listings_db()

def craigslist_soup(region, term, parser):
    url = "https://{region}.craigslist.org/search/sss?query={term}".format(
        region=region, term=term
    )

    response = requests.get(url=url)
    soup = b_s(response.content, parser)

    return soup


c_l = craigslist_soup(region="sfbay", term="planter", parser="html.parser")

def get_links_and_posts(input):
    posts = input.find_all("li", class_="result-row")
    links_and_posts = {}
    links = []
    for post in posts:
        title_class = post.find("a", class_="result-title hdrlnk")
        links.append(title_class["href"])
    links_and_posts = {"links": links, "posts": posts}
    return links_and_posts

get_links_and_posts(c_l)

def search_query(craigslist_soup):

    links = get_links_and_posts(c_l)["links"]  
    posts = get_links_and_posts(c_l)["posts"]
    posting_body = []
    list_results = [] 
    for link in links: 
        response_link = requests.get(url=link)
        link_soup = b_s(response_link.content, "html.parser")
        section_body_class = link_soup.find("section", id="postingbody")
        section_body_class_text = section_body_class.text
        if section_body_class_text is not None:
            section_body_class_text = section_body_class.text
        else:
            section_body_class_text = 'No description provided'
        stripped = section_body_class_text.replace("\n\nQR Code Link to This Post\n", "")
        final_strip = stripped.replace("\n\n", "")
        posting_body.append(final_strip)
    print(f' *****posting body is {posting_body}')
    for index, post in enumerate(posts):
        planter_description = posting_body[index]
        result_price = post.find("span", class_="result-price")
        result_price_text = result_price.get_text()
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
        result_listings = {
            "datetime": datetime,
            "cl_id": cl_id,
            "title_text": title_text,
            "price": result_price_text,
            "neighborhood_text": neighborhood_text,
            "url": url,
            "description": planter_description,
        }
        list_results.append(result_listings)
    return list_results 


def insert_into_db(result_dictionary):
    c = connect_to_db("listings.db") 
    for item in result_dictionary:
        c[0].execute(
            "INSERT OR REPLACE INTO listings VALUES(?,?,?,?,?,?,?)",
            (
                item['cl_id'],
                item['datetime'],
                item['title_text'],
                item['price'],
                item['neighborhood_text'],
                item['url'],
                item['description'],
            ),
        )
        c[1].commit()


insert_into_db(search_query(craigslist_soup=c_l)) 

def insert_into_csv(result_dictionary): 
    with open("listings.csv", "a") as csvfile:
        fieldnames = [
            "id",
            "created",
            "name",
            "price",
            "location",
            "url",
            "description",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        for item in result_dictionary:
            writer.writerow(
                {
                    "id": item['cl_id'],
                    "created": item['datetime'],
                    "name": item['title_text'],
                    "price": item['price'],
                    "location": item['neighborhood_text'],
                    "url": item['url'],
                    "description": item['description']
                }
            )
    num_rows = 0
    for row in open("listings.csv"):
        num_rows += 1
    print(num_rows)
    csvfile.close()


insert_into_csv(search_query(craigslist_soup=c_l))

def post_to_slack(result_dictionary):

    client = WebClient(SLACK_TOKEN) 
    desc = ''
    last_scrape = '2020-09-26 17:00'
    for item in result_dictionary: 
        # print(item['datetime']) 
        if last_scrape <= item['datetime']:
            print(item['datetime']) 
            desc = f" {item['cl_id']} | {item['price']} | {item['datetime']} | {item['title_text']} | {item['url']} | {item['neighborhood_text']} | {item['description']}"
            response = client.chat_postMessage(channel=SLACK_CHANNEL, text=desc,)
    print("{}: Got {} results".format(time.ctime(), len(result_dictionary)))
    time.sleep(5000)


post_to_slack(search_query(craigslist_soup=c_l))



# def post_to_slack(result_dictionary):

#     client = WebClient(SLACK_TOKEN) 
#     desc = ''
#     # while True:
#     #     time.sleep(5)
#     with open("listings.csv") as f:
#         cs_file = csv.reader(f)
#         print(f'cs file is {cs_file}')
#         for item in result_dictionary:
#             # print(f'item is{item}')
#             if item not in cs_file:
#                 # print('****HELLO****')
#                 desc = f" {item['cl_id']} | {item['datetime']} | {item['title_text']} | {item['url']} | {item['neighborhood_text']} | {item['description']}"
#                 response = client.chat_postMessage(channel=SLACK_CHANNEL, text=desc,)
#             else:
#                 print('item already in csv file')
#     print("{}: Got {} results".format(time.ctime(), len(result_dictionary)))


# post_to_slack(search_query(craigslist_soup=c_l))
