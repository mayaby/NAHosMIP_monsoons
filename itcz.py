import xarray as xr
import numpy as np


## function for calculating the itcz from a previously created zonal mean file (see cdo_examples.sh for the cdo commands)
def save_itcz(zmeanfile,ofile,lon=False,pr_key='pr'):
    zmean = xr.open_dataset(zmeanfile).squeeze()[pr_key]
    if lon:
        lats = zmean.lat
        ztot = zmean.sum(dim='lat').values
    else:
        lats = zmean.latitude
        ztot = zmean.sum(dim='latitude').values

    itcz_lats = np.divide(np.dot(zmean,lats),ztot)
    itcz = xr.Dataset(
        data_vars = dict(
            itcz = (['time'],itcz_lats)),
        coords = dict(
                time        = zmean.time)
    )
    itcz.to_netcdf(ofile)