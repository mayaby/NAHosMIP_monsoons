from cdo import * 
from functions import *
cdo = Cdo()
import os
import glob
import xarray as xr
import numpy as np

def get_dry_map(aprcp_box,cprcp_box,q=0.5,lon=True):
## for each box, this function first calculates the dry season quantiles, then gets the values below the limit, 
## and then counts the months and gets the total precipitation amount in those months
    if lon:
        adry_lim = aprcp_box.quantile(q,dim=['time','lat','lon'])
        cdry_lim = cprcp_box.quantile(q,dim=['time','lat','lon'])
    else:
        adry_lim = aprcp_box.quantile(q,dim=['time','latitude','longitude'])
        cdry_lim = cprcp_box.quantile(q,dim=['time','latitude','longitude'])

    adlen = aprcp_box.where(aprcp_box<adry_lim).groupby('time.year').count(dim='time').to_dataset(name='adlen')
    cdlen1 =  cprcp_box.where(cprcp_box<adry_lim).groupby('time.year').count(dim='time').to_dataset(name='cdlen1')
    cdlen2 =  cprcp_box.where(cprcp_box<cdry_lim).groupby('time.year').count(dim='time').to_dataset(name='cdlen2')

    adprcp = aprcp_box.where(aprcp_box<adry_lim).groupby('time.year').sum(dim='time').to_dataset(name='adprcp')
    cdprcp1 =  cprcp_box.where(cprcp_box<adry_lim).groupby('time.year').sum(dim='time').to_dataset(name='cdprcp1')
    cdprcp2 =  cprcp_box.where(cprcp_box<cdry_lim).groupby('time.year').sum(dim='time').to_dataset(name='cdprcp2')    

    len = adlen.merge(cdlen1.merge(cdlen2))
    prcp = adprcp.merge(cdprcp1.merge(cdprcp2))

    return len.merge(prcp)

def get_wet_map(aprcp_box,cprcp_box,q=0.7,lon=True):
    if lon:
        awet_lim = aprcp_box.quantile(q,dim=['time','lat','lon'])
        cwet_lim = cprcp_box.quantile(q,dim=['time','lat','lon'])
    else:
        awet_lim = aprcp_box.quantile(q,dim=['time','latitude','longitude'])
        cwet_lim = cprcp_box.quantile(q,dim=['time','latitude','longitude'])

    awlen = aprcp_box.where(aprcp_box>awet_lim).groupby('time.year').count(dim='time').to_dataset(name='awlen')
    cwlen1 =  cprcp_box.where(cprcp_box>awet_lim).groupby('time.year').count(dim='time').to_dataset(name='cwlen1')
    cwlen2 =  cprcp_box.where(cprcp_box>cwet_lim).groupby('time.year').count(dim='time').to_dataset(name='cwlen2')

    awprcp = aprcp_box.where(aprcp_box>awet_lim).groupby('time.year').sum(dim='time').to_dataset(name='awprcp')
    cwprcp1 =  cprcp_box.where(cprcp_box>awet_lim).groupby('time.year').sum(dim='time').to_dataset(name='cwprcp1')
    cwprcp2 =  cprcp_box.where(cprcp_box>cwet_lim).groupby('time.year').sum(dim='time').to_dataset(name='cwprcp2')    

    len = awlen.merge(cwlen1.merge(cwlen2))
    prcp = awprcp.merge(cwprcp1.merge(cwprcp2))

    return len.merge(prcp)


if __name__ == "__main__":
    model_names = ['HadGEM3-GC3-1MM','CanESM5','CESM2','IPSL-CM6A-LR']
    tos_keys = dict(zip(model_names,['tos','tos','TS','tos']))
    prcp_keys = dict(zip(model_names,['precipitation_flux','pr','PRECC','pr']))
    lat_keys = [False,True,True,True]

    aidcs = [[0,80*12],[0,80*12],[0+11,80*12+11],[0,80*12]]
    cidcs = [[20*12,100*12],[20*12,100*12],[100*12+11,180*12+11],[60*12,140*12]]
    aslices1 = dict(zip(model_names,aidcs))
    cslices1 = dict(zip(model_names,cidcs))
    aslices = aslices1
    cslices = cslices1

    # model = 'IPSL-CM6A-LR'
    # model = 'CanESM5'
    # model = 'CESM2'
    region_dict = {
            'am':[360-85,360-30,-20,11],
            'wam': [360-20,35,-10,25],
            'ism': [70, 85, 5, 25],
            'easm':[110,140,10,40]}

    for im, model in enumerate(model_names):
        print(model)
        aprcpm = xr.open_dataset('/p/tmp/mayayami/NAHosMIP/{}/vars/aprcpm_cont_Cgrid.nc'.format(model))[prcp_keys[model]][aslices[model][0]:aslices[model][1]]
        cprcpm = xr.open_dataset('/p/tmp/mayayami/NAHosMIP/{}/vars/cprcpm_cont_Cgrid.nc'.format(model))[prcp_keys[model]][cslices[model][0]:cslices[model][1]]
        for region, extent in region_dict.items():
            print(extent)
            aprcpm_box = get_box3(aprcpm,extent,lon=lat_keys[2],drop=True)
            cprcpm_box = get_box3(cprcpm,extent,lon=lat_keys[2],drop=True)

            q = 0.5
            for q in [0.4,0.5]:
                print('Dry season')
                admap = get_dry_map(aprcpm_box,cprcpm_box,lon=lat_keys[2],q=q)
                admap.to_netcdf('/p/tmp/mayayami/NAHosMIP/dry_maps/{}_dmap_{}_q{}_Cgrid.nc'.format(model,region,int(q*10)))

            q = 0.7
            for q in [0.7,0.6]:
                print('Wet season')
                awmap = get_wet_map(aprcpm_box,cprcpm_box,lon=lat_keys[2],q=q)
                awmap.to_netcdf('/p/tmp/mayayami/NAHosMIP/dry_maps/{}_wmap_{}_q{}_Cgrid.nc'.format(model,region,int(q*10)))
