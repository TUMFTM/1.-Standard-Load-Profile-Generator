from standard_load_profile_generator import main
import pandas as pd

"""
This is a sample application that demonstrates the use of this package.

"""

first_example_slp_df = main.get(
    start=pd.to_datetime('2020-01-20 00:00:00'),
    end=pd.to_datetime('2020-01-27 00:00:00'),
    slp_type='G1',
    country='DE',
    state='all_states',
    annual_energy_consumption=500)

second_example_slp_df = main.get(
    start=pd.to_datetime('2020-01-20 00:00:00'),
    end=pd.to_datetime('2020-01-27 00:00:00'),
    slp_type='G1',
    country='DE',
    state='DE-BY',
    annual_energy_consumption=5)

