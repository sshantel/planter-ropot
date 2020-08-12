import requests

url = 'https://sfbay.craigslist.org/'

headers ={'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}

response = requests.get(url=url, headers=headers)

print(response)
print(response.headers)
print(response.url)
print(response.content)