import requests

url = "https://sfbay.craigslist.org/search/sss?query=pot+%7C+planter+%7C+raised+bed+%7C+garden+bed&sort=rel&hasPic=1"

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
# print(posts[0])
first_cl_price = first_cl_result.a.text
print(f"first result price is {first_cl_price}")

first_cl_time_class = first_cl_result.find("time", class_="result-date")
print(f"first craigslist time class is {first_cl_time_class}")
first_cl_datetime = first_cl_time_class["datetime"]
print(f"date is {first_cl_datetime}")
first_cl_title_class = first_cl_result.find("a", class_="result-title hdrlnk")
print(f"first cl title class is {first_cl_title_class}")
first_cl_link = first_cl_title_class["href"]
print(f"first_cl_link is {first_cl_link}")
first_cl_id = first_cl_title_class["data-id"]
print(first_cl_id)
first_cl_title_text = first_cl_title_class.text
print(f" title is {first_cl_title_text}")
first_cl_neighborhood = first_cl_result.find("span", class_="result-hood")
print(first_cl_neighborhood.text)
