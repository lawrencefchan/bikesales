
# %%

from bs4_scrape import scrape_data
from create_db import query_db, write_to_db


def check_data(df, df_dims):
    ''' Check df
    `name` is a concat of '{year} {brand} {model}'
    '''

    # check that model is always included in name
    assert all([x[0] in x[1]
                if x[0] is not None else False
                for x in zip(df['model'], df['name'])])

    ''' Check df_dims
    `model` is a unique identifier for brand and bodyType
    '''
    assert df_dims['model'].value_counts().max() == 1

    return


scrape_db = False
update_db = False

if scrape_db:
    df_fact, df_dims = scrape_data(2)

    if update_db:
        write_to_db(df_fact, 'listings_fact')
        write_to_db(df_dims, 'model_dims')
else:
    df_fact = query_db('SELECT * from listings_fact')
    df_dims = query_db('SELECT * from model_dims')


print(df_fact)
