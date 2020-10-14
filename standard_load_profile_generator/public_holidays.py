import pandas as pd
import os.path
from requests.exceptions import HTTPError
import requests
import warnings
import sys


def get(year: int,
        country: str,
        state: str) -> pd.DataFrame:

    """
    Getting public holidays based on country and state from https://date.nager.at/

    :param year: year of requested public holidays
    :param country: country code of requested public holidays; for example 'DE' = Germany
                    (see https://date.nager.at/api/v2/publicholidays/)
    :param state: state code of requested public holidays; for example 'DE-BY' = Bavaria
                  (see https://date.nager.at/api/v2/publicholidays/)
    :return: pandas dataframe containing public holidays data

    """

    api_url = 'https://date.nager.at/api/v2/publicholidays/'

    my_path = os.path.dirname(os.path.realpath(__file__))
    my_path = os.path.join(my_path, 'data', str(country), 'public_holidays', 'ph-' + str(year) + '.pkl')

    if os.path.exists(my_path):
        df = pd.read_pickle(my_path)
    else:
        try:
            url = api_url + str(year) + '/' + str(country)
            r = requests.get(url=url)
            r.raise_for_status()
        except HTTPError as http_err:
            warnings.warn('public holidays api could not be reached | error: ' + str(http_err))
            sys.exit(1)
        except Exception as err:
            warnings.warn('public holidays api could not be reached | error: ' + str(err))
            sys.exit(1)
        else:
            j = r.json()
            df = pd.DataFrame.from_dict(j)
    if state == 'all_states':
        df = df.loc[df['global']]

    else:
        state_valid = ('=' + df['counties'].str.join('=') + '=').str.contains('=' + str(state) + '=')
        state_valid.fillna(False, inplace=True)
        if not state_valid.any():
            warnings.warn('state ' + str(state) + ' not found!')
            sys.exit(1)

        for row in df.loc[df.counties.isnull(), 'counties'].index:
            df.at[row, 'counties'] = []
        df = df[df.counties.apply(lambda x: state in x) | df['global']]

    df['date'] = pd.Series(pd.to_datetime(df['date'])).dt.date

    return df
