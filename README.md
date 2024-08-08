# Code for Ben-Yami et al. 2024 (Earth's Future)

This repository contains the jupyter notebooks used to produce the figures in "Impacts of AMOC collapse on monsoon rainfall: a
multi-model comparison", as well as some example scripts for the rest of the analysis. 

Some of the data from the NAHosMIP is available here: https://zenodo.org/records/7324394. However, most of the precipitation, temperature and wind data used in this study is only available on request. If you'd like to use the data, please email Laura Jackson at laura.jackson@metoffice.gov.uk. 

## Example scripts

- cdo_examples.sh : examples of the cdo commands used to process the data
- itcz.py : function to calculate the itcz from a zonal mean precipitation file
- get_seasons.py : script to calculate the dry and wet season lengths and precipitation
- SNS.py : script to calculate the SNS index (used in Figure S9)
- DNS_seas.py : script to calculate the DNS index for each month's climatological mean (used in Figure S10)
- functions.py : extra functions used in the jupyter notebooks

## Jupyter notebooks

- Main_plots.ipynb : notebook for the figures in the main text
- SI_plots.ipynb : notebook for the figures in the SI
- Get_stippling_regions.ipynb : notebook to get the stippled regions for Figures 4, S4, S7, S8
- SI_tables.ipynb : notebook for calculating the data in Tables S1, S3 and S5 (also used in Figure 3)




