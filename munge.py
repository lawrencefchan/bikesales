def get_url_from_id(row) -> str:
    '''
    Returns url string built by concatenating domain name/path, year, brand,
    model, my, and url_id.
    'https://www.bikesales.com.au/bikes/details/1975-suzuki-a100/SSE-AD-7492310/'

    NOTE: Many models have special characters, e.g.:
    * cb900f hornet (919cc)
    * YZF1000R - Thunderace

    NOTE: much easier to check function integrity at the data ingestion step,
    *before* table normalisation
    '''
    path = 'https://www.bikesales.com.au/bikes/details/'

    yr, brand, model, my, url_id = row
    model = (model.replace(')', '')
             .replace('(', '')
             .replace(' - ', '-')
             .replace(' ', '-'))

    join_strs = [str(yr), brand.lower(), model.lower()]

    if my != '':
        join_strs += [f'my{my}']

    # Note empty str to add trailing slash
    return '/'.join([path+'-'.join(join_strs), url_id, ''])


def get_my(s: str) -> str:
    '''
    Checks if url is suffixed by -myXX and if so, returns XX
    '''
    suffix = s.split('/')[-3].split('-')[-1]

    if suffix[:2] == 'my':
        return suffix[-2:]
    else:
        return ''


def munge_fact_table(df, df_dims):
    df['year'] = df['name'].str[:4].astype(int)  # get model year
    assert not df['flagged'].any()  # TODO: handle these cases

    df = df.merge(df_dims[['modelId', 'model']], on='model') \
           .drop(['name', 'model', 'brand', 'bodyType', 'flagged'], axis=1)

    df['url_id'] = df['url'].apply(lambda x: x.split('/')[-2])
    df['my'] = df['url'].apply(get_my)

    df = df.drop('url', axis=1)

    return df


def munge_dim_table(df):
    '''
    TODO: check existing db for duplicates
    '''

    df_dims = df[['model', 'brand', 'bodyType']].drop_duplicates()

    df_dims['modelId'] = df_dims.index + 100000
    return df_dims
