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


def write_model_dims(df):
    # create new db and make connection
    con = sqlite3.connect('bikesales.sqlite')
    df.to_sql('model_dims', con, if_exists='replace', index=False)
    con.commit()
    con.close()


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


def write_listings_fact(df):
    con = sqlite3.connect('bikesales.sqlite')
    df.to_sql('listings_fact', con, if_exists='replace', index=False)
    con.commit()
    con.close()


def test_query(query_str=None):
    # test whether the write was successful

    # TODO: try not to use pandas here
    # check cost of importing libraries multiple times

    con = sqlite3.connect('bikesales.sqlite')

    if query_str is None:
        query_str = 'SELECT * from listings_fact LIMIT 5'
        print(pd.read_sql_query(query_str, con))
    else:
        df = pd.read_sql_query(query_str, con)

    con.close()

    return df


if __name__ == '__main__':
    df = test_query('SELECT * from listings_fact')
    df_dims = test_query('SELECT * from model_dims')

# %%
d = df_dims.merge(df, on='modelId')


# %%

'https://www.bikesales.com.au/bikes/details/1975-suzuki-a100/SSE-AD-7492310/'
#  ['2007-honda-cb900f-hornet-919cc', 'SSE-AD-7492274'],


details = (d['year'].astype(str) + '-'
           + d['brand'] + '-'
           + d['model'].replace({
                '\)': '',  # NOTE: parentheses need to be escaped
                '\(': '',
                ' ': '-'
           }, regex=True))

# %%

comparison = pd.concat([
    details.str.lower(),
    d['url'].str.split('/', expand=True)[5]
    ], axis=1)

comparison.head()

comparison[comparison[0] != comparison[5]]

'''
url includes myXX for certain links e.g. 2008-honda-cbr125r-my09

possible solution is to truncate everything after the [year-brand-model] including
the detail code (e.g. SSE-AD-7492310) and append that to the url
'''
