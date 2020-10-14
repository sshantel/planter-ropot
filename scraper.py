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
import sys
import traceback

SLACK_TOKEN = os.environ["SLACK_API_TOKEN"]
SLACK_CHANNEL = "#planter_ropot"


def connect_to_db(name_of_db):
    conn = sqlite3.connect(name_of_db)
    c = conn.cursor()
    return (c, conn)

def get_last_scrape(): 
    with open("listings.csv", newline='') as csvfile:
        last_scrape = '' 
        df = pd.read_csv('listings.csv') 
        print(f'df is {df}') 
        if not df.empty:   
            last_scrape = df['created'].max()  
            last_scrape = pd.to_datetime(last_scrape)
        else:
            last_scrape = datetime.now() - timedelta(hours=2)  
        print(f'FIRST CALL last_scrape is {last_scrape}')

    return last_scrape

get_last_scrape()

def craigslist_soup(region, term, last_scrape):
    print(f'craigslist soup {last_scrape}')
    url = "https://{region}.craigslist.org/search/sss?query={term}".format(
        region=region, term=term
    )
    response = requests.get(url=url) 
    soup = b_s(response.content, 'html.parser')
    posts = soup.find_all("li", class_="result-row") 
    links = []
    image_jpg_list = []
    posting_body = []
    list_results = []
    for post in posts:
        title_class = post.find("a", class_="result-title hdrlnk")
        links.append(title_class["href"]) 
    for link in links: 
        response_link = requests.get(url=link)
        link_soup = b_s(response_link.content, "html.parser")
        image_url = link_soup.find('img')
        if image_url is not None:
            image_url = image_url['src'] 
        else:
            image_url = 'no image provided in this listing'
        image_jpg_list.append(image_url)
        section_body_class = link_soup.find("section", id="postingbody")
        if section_body_class is not None:
            section_body_class = section_body_class.get_text()
        else:
            section_body_class = 'No description provided'
        stripped = section_body_class.replace("\n\nQR Code Link to This Post\n", "")
        final_strip = stripped.replace("\n\n", "")
        posting_body.append(final_strip)  
    for index, post in enumerate(posts):
        # print(index,post)
        planter_description_full = posting_body[index] 
        image_url_jpg = image_jpg_list[index]
        result_price = post.find("span", class_="result-price")
        result_price_text = result_price.get_text()
        time_class = post.find("time", class_="result-date")
        created_at = time_class["datetime"]
        title_class = post.find("a", class_="result-title hdrlnk")
        url = title_class["href"]
        cl_id = title_class["data-id"]
        title_text = title_class.text
        neighborhood = post.find("span", class_="result-hood")
        if neighborhood is not None:
            neighborhood_text = neighborhood.get_text()
        else:
            neighborhood_text == "No neighborhood provided"
        result_listings = {
            "cl_id": cl_id,
            "created_at": created_at,
            "title_text": title_text,
            "price": result_price_text,
            "neighborhood_text": neighborhood_text,
            "url": url,
            "description": planter_description_full,
            "jpg": image_url_jpg,
        }  

        if pd.to_datetime(result_listings['created_at']) > pd.to_datetime(last_scrape):
            list_results.append(result_listings)
            print(f'the listing was posted at {created_at} and the last scrapetime was {last_scrape} so we will append this')
        else:  
            print(f'the listing was posted at {created_at} and the last scrapetime was {last_scrape} so we will NOT append this')
    print(list_results)
    print(f'last SCRAPE is {last_scrape}')
    return list_results 

craigslist_soup(region='sfbay',term='planter', last_scrape=get_last_scrape())

c_l = craigslist_soup(region='sfbay', term='planter',last_scrape=get_last_scrape())


def create_csv_db():
    with open("listings.csv", "w", newline="") as csvfile:
        csv_headers = ["id", "created", "name", "price", "location", "url", "description", "jpg"]
        writer = csv.DictWriter(csvfile, fieldnames=csv_headers)
        writer.writeheader()
    with open("scrapings.csv", "w", newline="") as csvfile:
        csv_headers = ["last scrape", "results scraped"]
        writer = csv.DictWriter(csvfile, fieldnames=csv_headers)
        writer.writeheader()
    c = connect_to_db("listings.db")
    c[0].execute(
        """CREATE TABLE IF NOT EXISTS listings
                (id TEXT PRIMARY KEY,
                created TEXT,
                name TEXT,
                price TEXT,
                location TEXT,
                url TEXT UNIQUE,
                description TEXT,
                jpg TEXT)"""
    )
create_csv_db()

def insert_into_csv_db(result_listings, last_scrape): 
    #add to listings csv 
    with open("listings.csv", "a") as csvfile:
        fieldnames = [
            "id",
            "created",
            "name",
            "price",
            "location",
            "url",
            "description",
            "jpg",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        for item in result_listings: 
            writer.writerow(
                {
                    "id": item['cl_id'],
                    "created": item['created_at'],
                    "name": item['title_text'],
                    "price": item['price'],
                    "location": item['neighborhood_text'],
                    "url": item['url'],
                    "description": item['description'],
                    "jpg": item["jpg"]
                }
            )
    csvfile.close()
    #add to scrapings csv 

    with open("scrapings.csv", "a") as csvfile:
        fieldnames = [
            "last scrape",
            "results scraped", 
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow(
            {
                'last scrape': last_scrape, 
                'results scraped': len(result_listings),
            }
        ) 
    csvfile.close()

    c = connect_to_db("listings.db") 
    for item in result_listings:   
        c[0].execute(
            "INSERT OR REPLACE INTO listings VALUES(?,?,?,?,?,?,?,?)",
            (
                item['cl_id'],
                item['created_at'],
                item['title_text'],
                item['price'],
                item['neighborhood_text'],
                item['url'],
                item['description'],
                item['jpg'],            ),
        )
        c[1].commit()

insert_into_csv_db(result_listings=c_l, last_scrape=get_last_scrape())

def post_to_slack(result_listings):
    client = WebClient(SLACK_TOKEN) 
    print(f'client is {client}')  
    print(f'slack result listings {result_listings}')
    for item in result_listings:     
        sliced_description = item['description']
        sliced_description = sliced_description[:100] + '...'
        desc = f" {item['cl_id']} | {item['price']} | {item['created_at']} | {item['title_text']} | {item['url']} | {item['neighborhood_text']} | {sliced_description} | {item['jpg']}  "
        response = client.chat_postMessage(channel=SLACK_CHANNEL, text=desc) 
    print("End scrape {}: Got {} results".format(datetime.now(), len(result_listings)))
result_listings = c_l
schedule.every(1).hour.do(post_to_slack, result_listings) 

if __name__ == "__main__": 
    while True:
        print("Starting scrape cycle of planters in the SF Bay Area: {}".format(time.ctime()))
        try:
            connect_to_db('listings.db')
            get_last_scrape()
            craigslist_soup(region='sfbay',term='planter', last_scrape=get_last_scrape())
            create_csv_db()
            insert_into_csv_db(result_listings=c_l, last_scrape=get_last_scrape())
            post_to_slack(result_listings) 
        except KeyboardInterrupt:
            print("Exiting....")
            sys.exit(1)
        except Exception as exc:
            print("Error with the scraping:", sys.exc_info()[0])
            traceback.print_exc()
        else:
            in_one_hour = datetime.now() + timedelta(hours=1)
            print(in_one_hour)
            print("{}: Successfully finished scraping. Next scrape will be at {} ".format(time.ctime(), in_one_hour)) 
        schedule.run_pending()
        time.sleep(2400) 