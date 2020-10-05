import requests
import os

from slack import WebClient

from bs4 import BeautifulSoup as b_s

import csv
import operator
import pandas as pd

import sqlite3
 
import time
from datetime import datetime, date, timedelta 
import schedule

SLACK_TOKEN = os.environ["SLACK_API_TOKEN"]
SLACK_CHANNEL = "#planter_ropot"


def connect_to_db(name):
    conn = sqlite3.connect(name)
    c = conn.cursor()
    return (c, conn)

def create_listings_csv():
    with open("listings.csv", "w", newline="") as csvfile:
        csv_headers = ["id", "created", "name", "price", "location", "url", "description"]
        writer = csv.DictWriter(csvfile, fieldnames=csv_headers)
        writer.writeheader()
create_listings_csv()

def create_scrapings_csv():
    with open("scrapings.csv", "w", newline="") as csvfile:
        csv_headers = ["last scrape", "results scraped"]
        writer = csv.DictWriter(csvfile, fieldnames=csv_headers)
        writer.writeheader()
create_scrapings_csv()

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
            section_body_class_text = section_body_class.get_text()
        else:
            section_body_class_text = 'No description provided'
        stripped = section_body_class_text.replace("\n\nQR Code Link to This Post\n", "")
        final_strip = stripped.replace("\n\n", "")
        posting_body.append(final_strip)
    print(f' *****posting body is {posting_body}')
    for index, post in enumerate(posts):
        planter_description_full = posting_body[index]
        planter_description = planter_description_full[:100] + '...'
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
            "cl_id": cl_id,
            "datetime": datetime,
            "title_text": title_text,
            "price": result_price_text,
            "neighborhood_text": neighborhood_text,
            "url": url,
            "description": planter_description_full,
        } 
        if since_last_scrape(result_listings['datetime']):
            list_results.append(result_listings)
        else: 
            continue  
    return list_results 
 
def insert_into_listings_csv(result_dictionary): 
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
    csvfile.close()

 
def since_last_scrape(datetime): 
    print(f'datetimeis {datetime}')  
    date_time_obj = pd.to_datetime(datetime)
    print(f'date time obj is {date_time_obj}') 
    df = pd.read_csv('listings.csv') 
    print(f'df is {df}')
    yesterday = date.today() - timedelta(days=1)
    print(f'yesterday is {yesterday}') 
    try: 
        last_scrape = df['created'].max()  
        last_scrape = pd.to_datetime(last_scrape)
        if last_scrape == pd.isnull():
            raise TypeError
    except TypeError:
        last_scrape = yesterday  
    return date_time_obj > last_scrape 

insert_into_listings_csv(search_query(craigslist_soup=c_l))

def insert_into_scrapings_csv(last_scrape, result_dictionary):
    print(f'last scrape is {last_scrape_obj}')
    with open("scrapings.csv", "a") as csvfile:
        fieldnames = [
            "last scrape",
            "results scraped", 
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow(
            {
                'last scrape': last_scrape, 
                'results scraped': len(result_dictionary),
            }
        )
    csvfile.close()
 

df = pd.read_csv('listings.csv') 
last_scrape = df['created'].max()  
last_scrape_obj = pd.to_datetime(last_scrape)

insert_into_scrapings_csv(since_last_scrape(datetime = last_scrape_obj), result_dictionary = search_query(craigslist_soup=c_l))


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

def post_to_slack(result_dictionary):

    client = WebClient(SLACK_TOKEN) 
    print(f'client is {client}')
    for item in result_dictionary: 
        print(item)
        desc = f" {item['cl_id']} | {item['price']} | {item['datetime']} | {item['title_text']} | {item['url']} | {item['neighborhood_text']} | {item['description']}"
        print(desc)
        response = client.chat_postMessage(channel=SLACK_CHANNEL, text=desc,)
        print(response)
    print("End scrape {}: Got {} results".format(datetime.now(), len(result_dictionary)))
result_dictionary = search_query(craigslist_soup=c_l)
schedule.every(60).seconds.do(post_to_slack, result_dictionary) 

 
if __name__ == "__main__":
    while True:  
        schedule.run_pending()  
        time.sleep(1) 
post_to_slack(host='0.0.0.0', debug=True, port=8080)
 