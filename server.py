import requests
import os
from slack import WebClient

SLACK_TOKEN = os.environ["SLACK_API_TOKEN"]
SLACK_CHANNEL = "#planter"

url = "https://sfbay.craigslist.org/search/sss?query=planter"

headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36"
}

response = requests.get(url=url, headers=headers)

# print(response)
# print(response.headers)
# print(response.url)
# print(response.content)

from bs4 import BeautifulSoup as b_s

craigslist_soup = b_s(response.content, "html.parser")
posts = craigslist_soup.find_all("li", class_="result-row")
first_cl_result = posts[0]
results = posts
# print(results)
for post in posts:
    price = post.a.text
    print(price)
    time_class = post.find("time", class_="result-date")
    datetime = time_class["datetime"]
    print(datetime)
    title_class = post.find("a", class_="result-title hdrlnk")
    link = title_class["href"]
    print(link)
    cl_id = title_class["data-id"]
    print(cl_id)
    title_text = title_class.text
    print(title_text)
    neighborhood = post.find("span", class_="result-hood")
    print(neighborhood)

# first_cl_price = first_cl_result.a.text
# print(f"first result price is {first_cl_price}")
# first_cl_time_class = first_cl_result.find("time", class_="result-date")
# print(f"first craigslist time class is {first_cl_time_class}")
# first_cl_datetime = first_cl_time_class["datetime"]
# print(f"date is {first_cl_datetime}")
# first_cl_title_class = first_cl_result.find("a", class_="result-title hdrlnk")
# print(f"first cl title class is {first_cl_title_class}")
# first_cl_link = first_cl_title_class["href"]
# print(f"first_cl_link is {first_cl_link}")
# first_cl_id = first_cl_title_class["data-id"]
# print(first_cl_id)
# first_cl_title_text = first_cl_title_class.text
# print(f" title is {first_cl_title_text}")
# first_cl_neighborhood = first_cl_result.find("span", class_="result-hood")
# print(first_cl_neighborhood.text)
# neighborhood = first_cl_neighborhood.text


client = WebClient(SLACK_TOKEN)
desc = f"|{price}| {title_text} | {datetime}|{link}|"
response = client.chat_postMessage(channel=SLACK_CHANNEL, text=desc,)
print(response)

