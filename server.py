import requests
import os

# from slack import WebClient
from bs4 import BeautifulSoup as b_s


SLACK_TOKEN = os.environ["SLACK_API_TOKEN"]
SLACK_CHANNEL = "#planter"


def search_query(region, term):
    url = f"https://{region}.craigslist.org/search/sss?query={term}".format(
        region=region, term=term
    )
    print(f"url is {url}")
    response = requests.get(url=url)
    print(response)

    craigslist_soup = b_s(response.content, "html.parser")
    # print(craigslist_soup[0])
    posts = craigslist_soup.find_all("li", class_="result-row")
    first_cl_result = posts
    # print(first_cl_result)
    links = []
    for post in posts:
        # print(post)
        title_class = post.find("a", class_="result-title hdrlnk")
        # print(f"title class is {title_class}")
        # print(title_class['href'])
        links.append(title_class["href"])
        # return links
        # print(links)
        for link in links:
            # print(f"link is {link}")
            response_link = requests.get(url=link)
            # print(f"response link is {response_link}")
            link_soup = b_s(response_link.content, "html.parser")
            print(f"this is link soup {link_soup}")
            section_body_class = link_soup.find("section", id="postingbody")
            print(f"this is section body class {section_body_class}")
            # print(section_body_class)
            print(section_body_class.text)
            cl_description = link_soup.find("div", class_="print-qrcode")
            # print(cl_description)
            # print(cl_description["data-location"])

    # print(first_cl_result)
    # results = posts
    # print(results)
    # for post in posts:
    #     price = post.a.text
    #     print(price)
    #     time_class = post.find("time", class_="result-date")
    #     datetime = time_class["datetime"]
    #     print(datetime)
    #     title_class = post.find("a", class_="result-title hdrlnk")
    #     link = title_class["href"]
    #     print(link)
    #     cl_id = title_class["data-id"]    #     print(cl_id)
    #     title_text = title_class.text
    #     print(title_text)
    #     neighborhood = post.find("span", class_="result-hood")
    #     print(neighborhood)

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
    # print(response)


search_query(region="sfbay", term="planter")

