'''
WIP: trying to get postgres functional
    * Seemingly working:
        * create table
        * INSERT INTO bikes (info) VALUES('{json_to_write}')
    * Not working:
        * pulling data back out (querying with "->")
        * saving using stringIO and copy_from (apparently muuuch more performant)
'''

# %%
import requests
from bs4 import BeautifulSoup
import json
import psycopg2
from io import StringIO


url = ('https://www.bikesales.com.au/bikes/?q=(And.('
       'Or.Make.BMW._.Make.Honda._.Make.Kawasaki._.Make.Suzuki._.Make.Triumph._.Make.Yamaha.)_.('
       'C.Type.Road._.(Or.SubType.Naked._.SubType.Super+Sport.))_'
       '.Price.range(..10000).)&sort=Price')

headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;',
           'Accept-Encoding': 'gzip',
           'Accept-Language': 'zh-CN,zh;q=0.8', 'Referer': 'http://www.example.com/',
           'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) '
           'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}


# --- run request
res = requests.get(url, headers=headers)

# # %% --- save soup to text file
# assert res.status_code == 200
# res.text

# with open('url_response.txt', 'w') as f:
#     f.write(res.text)

# # %% --- run bs4 from text file
# with open('url_response.txt') as f:
#     soup = BeautifulSoup(f.read())
# print(soup.prettify())

# --- run bs4 from memory
soup = BeautifulSoup(res.text, 'html.parser')
script = soup.find('script', {'type': 'application/ld+json'}).string

# --- get everything between start and end parenthesis
json_obj = json.loads(script[script.rfind('}')-1:script.find('{')+1])


def munge_nested_dict(d):
    # flatten dictionary and remove poo
    try :
        key = d['@type']
        if key == 'Brand':
            munged = d['name']
        elif key == 'QuantitativeValue':
            assert d['unitCode'] == 'KM'
            munged = d['value']
        elif key == 'EngineSpecification':
            munged = d['engineDisplacement']['value']
        elif key == 'Offer':
            munged = d['price']
            if d['priceCurrency'] != 'AUD':
                munged += d['priceCurrency']
    except (KeyError, AssertionError):
        munged = d
        raise
    finally:
        return munged


default_keys = ['@type',
                'url',
                'name',
                'model',
                'brand',
                'bodyType',
                'mileageFromOdometer',
                'vehicleEngine',
                'offers',
                'image']

# %%
conn = psycopg2.connect('dbname=bikesales user=postgres password=vcDZcbIpalmrTyr7Onf8')  # open connection

for i in json_obj['mainEntity']['itemListElement']:
    flagged = False  # add a flag to check entry manually

    try:  # check that keys are consistent
        assert (list(i['item'].keys()) == default_keys)
    except AssertionError:
        flagged = True
        continue

    for k, v in i['item'].items():
        if type(v) is dict:
            try:
                munged = munge_nested_dict(v)
            except Exception as e:
                print(e)
                flagged = True
            finally:
                i['item'][k] = munged

    i['item']['image'] = len(i['item']['image'])
    i['item']['flagged'] = flagged
    i['item'].pop('@type', None)


    # --- write data to postgres
    cur = conn.cursor()  # Open a cursor to perform database operations

    json_to_write = json.dumps(i['item'])
    cur.execute(f'''INSERT INTO bikes (info)
                VALUES('{json_to_write}');''')
    conn.commit()

    # # create table
    # cur.execute('''CREATE TABLE bikes (
    #             id serial NOT NULL PRIMARY KEY,
    #             info json NOT NULL)''')
    # conn.commit()

    cur.close()

conn.close()




# %% --- read, test from postgres


conn = psycopg2.connect('dbname=bikesales user=postgres password=vcDZcbIpalmrTyr7Onf8')  # open connection
cur = conn.cursor()  # Open a cursor to perform database operations

query = '''SELECT bikes -> 'offers' AS offers,
                  bikes -> 'name' AS name
           FROM bikes'''
cur.execute(query)

rows = cur.fetchall()
cur.close()
conn.close()

rows



# # %% loop through all pages

# for k, v in json_obj['mainEntity'].items():
#     print(k, v)
#     print('\n')

# # n_items = json_obj['mainEntity']['numberOfItems']

# # offset = 0
# # offset += len(json_obj['mainEntity']['itemListElement'])
# # offset = f'&offset={offset}'


# # %% --- append data from page to csv
# # i = 0
# # for k, v in json_obj['mainEntity']['itemListElement'][i]['item'].items():
# #     print(k, ':', v)
# #     print('\n')
