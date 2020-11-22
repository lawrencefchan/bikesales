# %%
import requests
from bs4 import BeautifulSoup


url = ('https://www.bikesales.com.au/bikes/?q=(And.('
        'Or.Make.BMW._.Make.Honda._.Make.Kawasaki._.Make.Suzuki._.Make.Triumph._.Make.Yamaha.)_.('
        'C.Type.Road._.(Or.SubType.Naked._.SubType.Super+Sport.))_'
        '.Price.range(..10000).)&sort=Price')

headers = {"Accept": "text/html,application/xhtml+xml,application/xml;", "Accept-Encoding": "gzip",
            "Accept-Language": "zh-CN,zh;q=0.8", "Referer": "http://www.example.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36"}

res = requests.get(url, headers=headers)

# %%
assert res.status_code == 200
res.text

with open('url_response.txt', 'w') as f:
  f.write(res.text)

# %% run bs4 from text file
with open("url_response.txt") as f:
    soup = BeautifulSoup(f.read())
print(soup.prettify())

# %% run bs4 from memory
soup = BeautifulSoup(res.text, 'html.parser')
# print(soup.prettify())


h2 = soup.find_all('script', {'type': 'application/ld+json'})
import json

# h2[0].contents[0]
h2[0].text

# get everything between start and end parenthesis
