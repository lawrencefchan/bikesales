
# %%

from bs4_scrape import scrape_data
from create_db import write_to_db


def munge_df(df, df_dims):
    df['year'] = df['name'].str[:4].astype(int)  # get model year
    assert not df['flagged'].any()  # TODO: handle these cases

    df = df.merge(df_dims[['modelId', 'model']], on='model') \
           .drop(['name', 'model', 'brand', 'bodyType', 'flagged'], axis=1)

    # TODO: compress URL

    return df


def munge_dim_table(df_dims):
    df_dims['modelId'] = df_dims.index + 100000
    return df_dims


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


df = scrape_data()
df_dims = df[['model', 'brand', 'bodyType']].drop_duplicates()

df_dims = munge_dim_table(df_dims)
df = munge_df(df, df_dims)

write_to_db(df, 'listings_fact')
write_to_db(df_dims, 'model_dims')
