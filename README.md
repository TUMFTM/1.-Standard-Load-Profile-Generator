# VDEW Standard Load Profile Generator 
This is a simple python module for generating standard load profiles on the basis of VDEW 
(see https://www.bdew.de/energie/standardlastprofile-strom/).

## Getting Started

1. Clone this project.
2. Copy the folder standard_load_profile_generator/standard_load_profile_generator wherever you want to use it.
3. Use function main.get(...) (see app.py for some examples) in order to get the desired standard load profile

## Running the module
Explain how to run the code
  
```
example_slp_df = main.get(
    start=pd.to_datetime('2020-01-20 00:00:00'),
    end=pd.to_datetime('2020-01-27 00:00:00'),
    slp_type='G1',
    country='DE',
    state='all_states',
    annual_energy_consumption=500)
```

## Deployment
The module requires an internet connection because public holidays are obtained via the public API 
https://date.nager.at/.

Built with [Python](https://www.python.org/) 3.6.1

## Authors
Adam Waclaw

## License
This project is licensed under the GNU LESSER GENERAL PUBLIC License - see the LICENSE.md file for details.

## Sources
[1] https://www.bdew.de/energie/standardlastprofile-strom/

[2] https://date.nager.at/