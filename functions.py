import numpy as np
import xarray as xr
from shapely.geometry.polygon import LinearRing
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy


def get_box(data,lon_min,lon_max,lat_min,lat_max,nav=False,lon=False):
    if nav:
        data_box = (
            data
            .where(data['nav_lon'] >= lon_min)
            .where(data['nav_lon'] <= lon_max)
            .where(data['nav_lat'] >= lat_min)
            .where(data['nav_lat'] <= lat_max))
        
    elif lon:
         data_box = (
            data
            .where(data['lon'] >= lon_min)
            .where(data['lon'] <= lon_max)
            .where(data['lat'] >= lat_min)
            .where(data['lat'] <= lat_max)
            )
    else:
        data_box = (
            data
            .where(data['longitude'] >= lon_min)
            .where(data['longitude'] <= lon_max)
            .where(data['latitude'] >= lat_min)
            .where(data['latitude'] <= lat_max)
        )
    return data_box

def is_month(month, im):
    return month == im

def get_box2(data,lon_min,lon_max,lat_min,lat_max,lon=False,drop=True):
#     if lon_min>180:
#         lon_min=lon_min-360
#     if lon_max>180:
#         lon_max=lon_max-360
    
    if lon_min > lon_max:
        if lon:
            data_box = (
                data
                .where((data['lon'] >= lon_min) | (data['lon'] <= lon_max),drop=drop)
                .where(data['lat'] >= lat_min,drop=drop)
                .where(data['lat'] <= lat_max,drop=drop))
        else:
            data_box = (
                data
                .where((data['longitude'] >= lon_min) | (data['longitude'] <= lon_max),drop=drop)
                .where(data['latitude'] >= lat_min,drop=drop)
                .where(data['latitude'] <= lat_max,drop=drop))
    else:
        if lon:
             data_box = (
                data
                .where(data['lon'] >= lon_min,drop=drop)
                .where(data['lon'] <= lon_max,drop=drop)
                .where(data['lat'] >= lat_min,drop=drop)
                .where(data['lat'] <= lat_max,drop=drop)
                )
        else:
            data_box = (
                data
                .where(data['longitude'] >= lon_min,drop=drop)
                .where(data['longitude'] <= lon_max,drop=drop)
                .where(data['latitude'] >= lat_min,drop=drop)
                .where(data['latitude'] <= lat_max,drop=drop)
            )
    return data_box

def get_box3(data,latlon,lon=True,drop=False):
    lon_min = latlon[0]
    lon_max = latlon[1]
    lat_min = latlon[2]
    lat_max = latlon[3]
    
    if lon_min > lon_max:
        if lon:
            data_box = (
                data
                .where((data['lon'] >= lon_min) | (data['lon'] <= lon_max),drop=drop)
                .where(data['lat'] >= lat_min,drop=drop)
                .where(data['lat'] <= lat_max,drop=drop))
        else:
            data_box = (
                data
                .where((data['longitude'] >= lon_min) | (data['longitude'] <= lon_max),drop=drop)
                .where(data['latitude'] >= lat_min,drop=drop)
                .where(data['latitude'] <= lat_max,drop=drop))
    else:
        if lon:
             data_box = (
                data
                .where(data['lon'] >= lon_min,drop=drop)
                .where(data['lon'] <= lon_max,drop=drop)
                .where(data['lat'] >= lat_min,drop=drop)
                .where(data['lat'] <= lat_max,drop=drop)
                )
        else:
            data_box = (
                data
                .where(data['longitude'] >= lon_min,drop=drop)
                .where(data['longitude'] <= lon_max,drop=drop)
                .where(data['latitude'] >= lat_min,drop=drop)
                .where(data['latitude'] <= lat_max,drop=drop)
            )
    return data_box

def get_box_avg(data,lon_min,lon_max,lat_min,lat_max,nav=False,lon=False):
    box = get_box(data,lon_min,lon_max,lat_min,lat_max,nav=nav,lon=lon)
    if nav:
        mean = box.mean(dim=['nav_lat','nav_lon']) 
    elif lon:
        mean = box.mean(dim=['lat','lon'])
    else:
        mean = box.mean(dim=['latitude','longitude'])
    return mean

def msel(data, im):
    return data.sel(time=is_month(data['time.month'],im)).resample(time="1YS").mean(dim="time")

def mavg(data):
    return data.groupby("time.month").mean(dim="time")

def mon_avg(data):
    avg = [np.array(data)[i::12].mean() for i in range(12)]
    return avg

def box_plot(latlon,col='#6a3d9a'):
    min_lon = latlon[0]
    max_lon = latlon[1]
    min_lat = latlon[2]
    max_lat = latlon[3]
    latsq = [min_lat, max_lat, max_lat, min_lat]
    lonsq = [min_lon, min_lon, max_lon, max_lon]
    ring = LinearRing(list(zip(lonsq, latsq)))
    ax.coastlines(linewidth=1)
    ax.add_feature(cartopy.feature.LAND, edgecolor='black',color='k')
    ax.add_geometries([ring], ccrs.PlateCarree(), facecolor='None', edgecolor=col,linewidth=5)

def box_plot2(latlon,col='#6a3d9a',lw=3,has=None):
    min_lon = latlon[0]
    
    max_lon = latlon[1]
    min_lat = latlon[2]
    max_lat = latlon[3]
    if min_lon>180:
        min_lon=min_lon-360
    if max_lon>180:
        max_lon=max_lon-360
    latsq = [min_lat, max_lat, max_lat, min_lat]
    lonsq = [min_lon, min_lon, max_lon, max_lon]
    ring = LinearRing(list(zip(lonsq, latsq)))
    ax.coastlines(linewidth=1)
    ax.add_feature(cartopy.feature.LAND, edgecolor='black',color='k')
    ax.add_geometries([ring], ccrs.PlateCarree(), facecolor='None', edgecolor=col,linewidth=lw,hatch=has)
    
def avg(data):
    return data.groupby("time.month").mean(dim="time")

def season_mean(ds, calendar="standard"):
    month_length = ds.time.dt.days_in_month
    weights = (
        month_length.groupby("time.season") / month_length.groupby("time.season").sum()
    )
    np.testing.assert_allclose(weights.groupby("time.season").sum().values, np.ones(4))
    return (ds * weights).groupby("time.season").sum(dim="time")

def yavg(data): # need to weigh the months by the number of days before averaging
    month_length = data.time.dt.days_in_month
    wgts = month_length.groupby("time.year") / month_length.groupby("time.year").sum()
    
    cond = data.isnull().groupby("time.year").sum()
    ones = xr.where(cond, np.nan, 1.0)
    
    avg = (data*wgts).groupby("time.year").sum()*ones
    
    return avg