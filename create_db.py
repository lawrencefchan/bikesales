# %%
import sqlite3
import pandas as pd

'''
NOTE:
reading from sqlite is much faster than writing, see benchmarks:
http://sebastianraschka.com/Articles/2013_sqlite_database.html#results-and-conclusions

It is probably fastest to pull a column from model dimensions and compare
it to 'model' column from df in memory. This avoids writing to df unnecessarily.
'''

def write_model_dims(d):
    # create new db and make connection
    con = sqlite3.connect('bikesales.sqlite')
    d.to_sql('model_dims', con, if_exists='replace', index=False)
    con.commit()
    con.close()


def write_listings_fact(df):
    con = sqlite3.connect('bikesales.sqlite')
    df.to_sql('listings_fact', con, if_exists='replace', index=False)
    con.commit()
    con.close()


def test_query():
    # test whether the write was successful
    # TODO: don't use pandas here
    # check cost of importing libraries multiple times

    con = sqlite3.connect('bikesales.sqlite')

    query_str = 'SELECT * from listings_fact LIMIT 5'
    test_df = pd.read_sql_query(query_str, con)

    print(test_df.head())

    con.close()
