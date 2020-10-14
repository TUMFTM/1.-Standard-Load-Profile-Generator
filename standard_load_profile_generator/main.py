import pandas as pd
from typing import Union
from os import path
import datetime
import os
import sys
import warnings
from . import public_holidays


def get(start: datetime.datetime,
        end: datetime.datetime,
        slp_type: str,
        country: str,
        state: str,
        annual_energy_consumption: Union[int, float] = 1) -> pd.DataFrame:

    """
    This is the main function of this package. It accepts the request, processed it and returns the requested standard
    load profile.

    :param start: timestamp of the first value of the standard load profile
    :param end: timestamp of the last value of the standard load profile
    :param slp_type: type of standard load profile like 'H0', 'G0', 'G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'L0', 'L1',
                     'L2'; more information https://www.bdew.de/energie/standardlastprofile-strom/
    :param country: country code of requested standard load profile; for example 'DE' = Germany
                    (see https://date.nager.at/api/v2/publicholidays/)
    :param state: state code of requested standard load profile; for example 'DE-BY' = Bavaria
                  (see https://date.nager.at/api/v2/publicholidays/)
    :param annual_energy_consumption: annual energy consumption in MWh to scale the normalized standard load profile
    :return: pandas dataframe (columns=['time', 'power']) containing the standard load profile in W
    """

    start = pd.to_datetime(start)
    end = pd.to_datetime(end)
    start_year = start.year
    end_year = end.year
    if start_year != end_year:
        year_lst = list(range(start_year, end_year + 1))
    else:
        year_lst = [start_year]

    my_path = os.path.dirname(os.path.realpath(__file__))
    my_path = os.path.join(my_path, 'data', str(country))
    if not path.exists(my_path):
        slp_df = pd.DataFrame()
        for y in year_lst:
            y_df = generate(slp_type, y, country, state)
            slp_df = pd.concat([slp_df, y_df])
    else:
        my_path = os.path.join(my_path, str(state))

        if not path.exists(my_path):
            slp_df = pd.DataFrame()
            for y in year_lst:
                y_df = generate(slp_type, y, country, state)
                slp_df = pd.concat([slp_df, y_df])
        else:
            my_path = os.path.join(my_path, str(slp_type))
            if not path.exists(my_path):
                slp_df = pd.DataFrame()
                for y in year_lst:
                    y_df = generate(slp_type, y, country, state)
                    slp_df = pd.concat([slp_df, y_df])
            else:
                slp_df = pd.DataFrame()
                for y in year_lst:
                    file_name = str(slp_type) + '-' + str(y) + '.pkl'
                    my_year_path = os.path.join(my_path, str(file_name))
                    if not path.exists(my_year_path):
                        y_df = generate(slp_type, y, country, state)
                        slp_df = pd.concat([slp_df, y_df])
                    else:
                        y_df = pd.read_pickle(my_year_path)
                        slp_df = pd.concat([slp_df, y_df])

    if (start is not None) & (end is not None):
        slp_df = slp_df.loc[(slp_df.time.dt.date >= start.date()) & (slp_df.time.dt.date <= end.date()), :]

    slp_df['power'] *= annual_energy_consumption
    slp_df['power'] = slp_df['power'].apply(lambda x: round(x, 1))

    slp_df.reset_index(inplace=True)
    slp_df.drop(['index'], axis=1, inplace=True)

    return slp_df


def generate(
        slp_type: str,
        year: int,
        country: str,
        state: str) -> pd.DataFrame:

    """
    This script generates the normalized standard load profile of the requested year on the basis of VDEW data
    (see https://www.bdew.de/energie/standardlastprofile-strom/)

    :param slp_type: type of standard load profile like 'H0', 'G0', 'G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'L0', 'L1',
                     'L2'; more information https://www.bdew.de/energie/standardlastprofile-strom/
    :param year: year of requested standard load profile
    :param country: country code of requested standard load profile; for example 'DE' = Germany
                    (see https://date.nager.at/api/v2/publicholidays/)
    :param state: state code of requested standard load profile; for example 'DE-BY' = Bavaria
                  (see https://date.nager.at/api/v2/publicholidays/)
    :return: pandas dataframe containing the normalized standard load profile of the requested year
    """

    my_path = os.path.dirname(os.path.realpath(__file__))
    my_path = os.path.join(my_path, 'data', 'slp.xls')

    try:
        slp_data_df = \
            pd.read_excel(my_path,
                          sheet_name=slp_type,
                          names=['time', 'winter_5', 'winter_6', 'winter_0', 'sommer_5', 'sommer_6', 'sommer_0',
                                 'ubgz_5', 'ubgz_6', 'ubgz_0'])
    except Exception as e:
        warnings.warn('could not read data for slp_type=' + str(slp_type) + ' | error: ' + str(e))
        sys.exit(1)

    slp_data_df.drop(slp_data_df.head(2).index, inplace=True)
    slp_data_df.drop(slp_data_df.tail(1).index, inplace=True)

    slp_data_df.sort_values(by='time', inplace=True)

    day_df = \
        pd.DataFrame(
            index=pd.date_range(start=str(year) + '-01-01', end=str(year) + '-12-31'))
    day_df.reset_index(inplace=True)
    day_df.columns = ['day']
    day_df['weekday'] = day_df.day.dt.dayofweek

    # consider public holidays (incl. Christmas Eve and New Years Eve)
    public_holidays_df = public_holidays.get(country=country, state=state, year=year)
    public_holidays_lst = public_holidays_df['date'].tolist()

    # set clock change
    day_df['clock_change_to_summer'] = False
    day_df['clock_change_to_winter'] = False
    sub = day_df.loc[day_df['day'] < (str(year) + '-04-01'), 'weekday']
    indx = sub.where(sub == 6).last_valid_index()
    day_df.at[indx, 'clock_change_to_summer'] = True
    sub = day_df.loc[day_df['day'] < (str(year) + '-11-01'), 'weekday']
    indx = sub.where(sub == 6).last_valid_index()
    day_df.at[indx, 'clock_change_to_winter'] = True

    if len(public_holidays_lst) > 0:
        day_df.loc[day_df['day'].isin(public_holidays_lst), 'weekday'] = 6
        day_df.loc[(day_df['day'] == (str(year) + '-12-24')) | (day_df['day'] == (str(year) + '-12-31')), 'weekday'] = 5
        day_df.loc[day_df.weekday < 5, 'weekday'] = 0
    else:
        sys.stderr.write('WARNING | no public holiday considered' + '\n')

    # set seasons
    day_df['season'] = 'ubgz'
    day_df.loc[(day_df.day <= (str(year) + '-03-20')) | (day_df.day >= (str(year) + '-11-01')), 'season'] = 'winter'
    day_df.loc[(day_df.day >= (str(year) + '-05-15')) & (day_df.day <= (str(year) + '-09-14')), 'season'] = 'sommer'

    # generate result dataframe
    res_df = pd.DataFrame(columns=['time', 'power'])

    for ind in day_df.index:
        df = slp_data_df[['time', str(day_df.at[ind, 'season']) + '_' + str(day_df.at[ind, 'weekday'])]].copy()
        df['day'] = day_df.at[ind, 'day']
        df['time'] = pd.Series(pd.to_datetime(df['day'].apply(str) + ' ' + df['time'].apply(str))).copy()
        df.drop(['day'], axis=1, inplace=True)
        df.columns = ['time', 'power']
        if day_df.at[ind, 'clock_change_to_summer']:
            df.set_index('time', inplace=True)
            df = df.drop(df.between_time('02:00', '02:45').index)
            df.reset_index(inplace=True)
        if day_df.at[ind, 'clock_change_to_winter']:
            df.set_index('time', inplace=True)
            df = pd.concat([
                df.between_time('00:00', '02:45'),
                df.between_time('02:00', '03:00'),
                df.between_time('03:15', '23:45')])
            df.reset_index(inplace=True)
        res_df = pd.concat([res_df, df])

    res_df.reset_index(inplace=True)
    res_df.drop(['index'], axis=1, inplace=True)

    # dynamic sampling of households
    if slp_type[:1] == 'H':
        res_df = dynamic_sampling_function(res_df)

    return res_df


def dynamic_sampling_function(df):

    df['day_no'] = df.time.dt.dayofyear
    a4 = -0.000000000392
    a3 = 0.00000032
    a2 = -0.0000702
    a1 = 0.0021
    a0 = 1.24
    fct_df = a4*(df['day_no']**4) + a3*(df['day_no']**3) + a2*(df['day_no']**2) + a1*df['day_no'] + a0
    df['power'] *= fct_df
    df.drop(['day_no'], axis=1, inplace=True)

    return df
