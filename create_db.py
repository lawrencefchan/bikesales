# %%
import sqlite3
import pandas as pd


'''
NOTE:
reading from sqlite is much faster than writing, see benchmarks:
http://sebastianraschka.com/Articles/2013_sqlite_database.html#results-and-conclusions

It is probably fastest to pull a column from model dimensions and compare it
to 'model' column from df in memory. This avoids writing to df unnecessarily.
'''


def write_to_db(df: pd.DataFrame, saveas: str):
    '''
    Save dataframe to sqlite database.

    Parameters
    ----
    df: dataframe to save
    saveas: table name to save as
    '''
    con = sqlite3.connect('bikesales.sqlite')
    df.to_sql(saveas, con, if_exists='replace', index=False)
    con.commit()
    con.close()


def query_db(query_str=None):
    '''
    Test whether the write was successful

    TODO: try not to use pandas here
    check cost of importing libraries multiple times
    '''
    con = sqlite3.connect('bikesales.sqlite')

    if query_str is None:
        query_str = 'SELECT * from listings_fact LIMIT 5'
        print(pd.read_sql_query(query_str, con))
    else:
        df = pd.read_sql_query(query_str, con)

    con.close()

    return df


if __name__ == '__main__':
    df_fact = query_db('SELECT * from listings_fact')
    df_dims = query_db('SELECT * from model_dims')

    # # -- one-off code to convert db format (trim url, add MY)
    # from munge import get_url_from_id, get_my

    # df_fact['url_id'] = df_fact['url'].apply(lambda x: x.split('/')[-2])
    # df_fact['my'] = df_fact['url'].apply(get_my)

    # # --- test that get_url works
    # d = df_dims.merge(df_fact, on='modelId')
    # zip_cols = ['year', 'brand', 'model', 'my', 'url_id']

    # get_url_list = [get_url_from_id(row) for
    #                 row in zip(*[d[c] for c in zip_cols])]
    # assert list(d['url']) == get_url_list

    # # --- rewrite df_fact to db, adding MY and url_id
    # df_fact = df_fact.drop('url', axis=1)
    # write_to_db(df_fact, 'listings_fact')
