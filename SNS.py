import xarray as xr
import numpy as np

model_names = ['HadGEM3-GC3-1MM','CanESM5','CESM2','IPSL-CM6A-LR']

aidcs = [[10*12,90*12],[0,80*12],[1*12,81*12],[0,80*12]]
cidcs = [[20*12,100*12],[20*12,100*12],[101*12,181*12],[60*12,140*12]]
aslicesm = dict(zip(model_names,aidcs))
cslicesm = dict(zip(model_names,cidcs))

def norm(u,v,i,j):
    Lo = u.shape[0]
    if i==0:
        nrm = np.sqrt(
            (v[Lo-1,j]**2 + u[Lo-1,j]**2 +
            4*(v[i,j]**2+u[i,j]**2) +
            v[i+1,j]**2+u[i+1,j]**2)*np.cos(np.radians(lats[j]))
            + (v[i,j-1]**2+u[i,j-1]**2)*np.cos(np.radians(lats[j-1]))
            + (v[i,j+1]**2+u[i,j+1]**2)*np.cos(np.radians(lats[j+1]))
        )
    elif i==(Lo-1):
        nrm = np.sqrt(
            (v[i-1,j]**2 + u[i-2,j]**2 +
            4*(v[i,j]**2+u[i,j]**2) +
            v[0,j]**2+u[0,j]**2)*np.cos(np.radians(lats[j]))
            + (v[i,j-1]**2+u[i,j-1]**2)*np.cos(np.radians(lats[j-1]))
            + (v[i,j+1]**2+u[i,j+1]**2)*np.cos(np.radians(lats[j+1]))
        )
    else:
        nrm = np.sqrt(
            (v[i-1,j]**2 + u[i-1,j]**2 +
            4*(v[i,j]**2+u[i,j]**2) +
            v[i+1,j]**2+u[i+1,j]**2)*np.cos(np.radians(lats[j]))
            + (v[i,j-1]**2+u[i,j-1]**2)*np.cos(np.radians(lats[j-1]))
            + (v[i,j+1]**2+u[i,j+1]**2)*np.cos(np.radians(lats[j+1]))
        )
    return nrm

### using files that are already at level 850 hPa

version = 'a'

for model in ['CESM2']:

    for version in ['a','c']:
            
        if version=='c':
            slicesm = cslicesm
        elif version=='a':
            slicesm = aslicesm

        vam = xr.open_dataset('/p/tmp/mayayami/NAHosMIP/{}/vars/{}vam.nc'.format(model,version)).V.squeeze()[slicesm[model][0]:slicesm[model][1]]
        uam = xr.open_dataset('/p/tmp/mayayami/NAHosMIP/{}/vars/{}uam.nc'.format(model,version)).U.squeeze()[slicesm[model][0]:slicesm[model][1]]
#     vam = xr.open_dataset('/p/tmp/mayayami/NAHosMIP/HadGEM3-GC3-1MM/vars/{}vam.nc'.format(version)).va.squeeze()
#     uam = xr.open_dataset('/p/tmp/mayayami/NAHosMIP/HadGEM3-GC3-1MM/vars/{}uam.nc'.format(version)).ua.squeeze()

# vam = xr.open_dataset('/p/tmp/mayayami/vwnd.mon.mean.nc').vwnd.sel(level=850)
# uam = xr.open_dataset('/p/tmp/mayayami/uwnd.mon.mean.nc').uwnd.sel(level=850)


## need to transpose because in formula (i,j) is (lon,lat)
        vam = vam.transpose('time','lon','lat')
        uam = uam.transpose('time','lon','lat')

        nt, Lo, La = vam.shape[0],vam.shape[1],vam.shape[2]
        lons = vam.lon.values
        lats = vam.lat.values

        va_clim = vam.groupby('time.month').mean('time')
        ua_clim = uam.groupby('time.month').mean('time')

        ## start with average, so no m,n

        v1 = va_clim[0]
        v7 = va_clim[6]
        u1 = ua_clim[0]
        u7 = ua_clim[6]

        v_minus = v1 - v7
        u_minus = u1 - u7

        v_mean = (v1+v7)/2
        u_mean = (u1+u7)/2

        Lo, La = u1.shape[0],u1.shape[1]

        top = np.full((Lo,La),np.nan)
        bottom = np.full((Lo,La),np.nan)


        for i, lon in enumerate(lons):
            for j, lat in enumerate(lats[1:-1]):
                top[i,j] = norm(u_minus, v_minus, i, j)
                bottom[i,j] = norm(u_mean, v_mean, i, j)

        sigma = top/bottom - 2

        sigma_array = v1.copy(data=sigma).rename('sigma')
        # sigma_array.to_netcdf('DNS/NCEPre_sigma.nc')
        sigma_array.to_netcdf('DNS/{}_{}va_sigma.nc'.format(model, version))