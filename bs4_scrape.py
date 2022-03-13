'''
Considerations:
    * How to determine bike condition?
    * What to do about duplicate entries scraped over multiple days?
    * How to tell between missing KMs & new bikes?

TODO:
    * NLP for scrapped/written-off/parts bikes
'''

# %%
import requests
from bs4 import BeautifulSoup
import json

import pandas as pd
from datetime import datetime


url = ('https://www.bikesales.com.au/bikes/?q=(And.('
       'Or.Make.BMW._.Make.Honda._.Make.Kawasaki._.Make.Suzuki._.Make.Triumph._.Make.Yamaha.)_.('
       'C.Type.Road._.(Or.SubType.Naked._.SubType.Super+Sport.))_'
       '.Price.range(..10000).)&sort=Price')

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;',
    'Accept-Encoding': 'gzip',
    'Accept-Language': 'zh-CN,zh;q=0.8', 'Referer': 'http://www.example.com/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'
    }

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


def get_page_content(offset):    
    # --- run request
    res = requests.get(url+f'&offset={offset}', headers=headers)
    assert res.status_code == 200

    soup = BeautifulSoup(res.text, 'html.parser')
    script = soup.find('script', {'type': 'application/ld+json'}).string

    # --- get everything between start and end parenthesis
    json_obj = json.loads(script[script.find('{')-1:script.rfind('}')+1])

    return json_obj


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


def munge_content(content: list) -> list:
    '''
    content : list
        json_obj['mainEntity']['itemListElement']
    
    Returns munged list with useless info deleted from content list
    '''
    arr = []

    for ix, d in enumerate(content):
        flagged = False  # add a flag to check entry manually

        try:  # check that keys are consistent
            assert all(x in list(d['item'].keys()) for x in default_keys)
        except AssertionError:
            flagged = True
            d['item']['flagged'] = flagged
            arr.append(d['item'])
            continue

        for k, v in d['item'].items():
            if type(v) is dict:
                try:
                    munged = munge_nested_dict(v)
                except Exception as e:
                    print(e)
                    flagged = True
                finally:
                    d['item'][k] = munged
                    continue

        d['item']['image'] = len(d['item']['image'])
        d['item']['flagged'] = flagged
        d['item'].pop('@type', None)

        arr.append(d['item'])

    return arr


def scrape_data():
    arr = []

    # --- first page (get number of items to scrape)
    page = 1
    json_obj = get_page_content(0)
    n_items = json_obj['mainEntity']['numberOfItems']

    arr += munge_content(json_obj['mainEntity']['itemListElement'])
    offset = len(json_obj['mainEntity']['itemListElement'])


    while offset < n_items and page < 100:  # scrape max n pages
        t_start = datetime.now()
        json_obj = get_page_content(offset)
        arr += munge_content(json_obj['mainEntity']['itemListElement'])
        offset += len(json_obj['mainEntity']['itemListElement'])
        page += 1
        print(f'Page {page}, scrape took {datetime.now() - t_start}')

    df = pd.DataFrame(arr)

    return df
