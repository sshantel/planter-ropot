import requests
import os

from slack import WebClient
from bs4 import BeautifulSoup as b_s

import csv 
import pandas as pd 

import time
from datetime import datetime, date, timedelta 
import schedule
import sys
import traceback

SLACK_TOKEN = os.environ["SLACK_API_TOKEN"]
SLACK_CHANNEL = "#planter_ropot"

def create_csv():
    if not os.path.isfile('listings.csv'):
        with open("listings.csv", "w", newline="") as csvfile:
            csv_headers = ["id", "created", "name", "price", "location", "url", "description", "jpg"]
            writer = csv.DictWriter(csvfile, fieldnames=csv_headers)
            writer.writeheader()
 
def get_last_scrape(): 
    with open("listings.csv", newline='') as csvfile:
        last_scrape = '' 
        df = pd.read_csv('listings.csv') 
        if not df.empty:   
            last_scrape = df['created'].max()  
            last_scrape = pd.to_datetime(last_scrape) 
 
    return last_scrape
 
def craigslist_soup(region, term, last_scrape): 
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
        print(post)
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

        if pd.isnull(pd.to_datetime(last_scrape)): 
            list_results.append(result_listings)
            print(f'the datetime is null. Listing posted {created_at} and last scrapetime {last_scrape} so we will append this AND POST TO SLACK')
        elif pd.to_datetime(result_listings['created_at']) > (pd.to_datetime(last_scrape)):
            list_results.append(result_listings)
            print(f'Listing posted {created_at} and last scrapetime {last_scrape} so we will append this AND POST TO SLACK')
        else:
            print(f'Listing posted {created_at} and last scrapetime {last_scrape}. We will not append this.')

    return list_results

def insert_into_csv_db(result_listings):
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
    
def post_to_slack(result_listings): 
    client = WebClient(SLACK_TOKEN)  
    for item in result_listings:     
        sliced_description = item['description']
        sliced_description = sliced_description[:100] + '...'
        desc = f"  {item['neighborhood_text']} | {item['created_at']} | {item['price']} | {item['title_text']} | {item['url']} | {sliced_description} | {item['jpg']} | {item['cl_id']}  "
        response = client.chat_postMessage(channel=SLACK_CHANNEL, text=desc) 
    print("End scrape {}: Got {} results".format(datetime.now(), len(result_listings)))

if __name__ == "__main__": 
    create_csv()

    while True:
        print("Starting scrape cycle of planters in the SF Bay Area: {}".format(time.ctime()))
        try:
            c_l = craigslist_soup(region='sfbay',term='planter', last_scrape=get_last_scrape())
            insert_into_csv_db(result_listings=c_l)
            post_to_slack(result_listings=c_l) 
            
        except KeyboardInterrupt:
            print("Exiting....")
            sys.exit(1)
        except Exception as exc:
            print("Error with the scraping:", sys.exc_info()[0])
            traceback.print_exc()
        
        in_ten_minutes = datetime.now() + timedelta(minutes=10) 
        print("{}: Successfully finished scraping. Next scrape will be at {} ".format(time.ctime(), in_ten_minutes)) 
        schedule.run_pending()
        time.sleep(600) 