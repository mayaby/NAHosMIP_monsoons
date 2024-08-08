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

def get_sigma(u_minus,v_minus,u_mean,v_mean):
    Lo, La = u_mean.shape[0],u_mean.shape[1]

    top = np.full((Lo,La),np.nan)
    bottom = np.full((Lo,La),np.nan)
    for i, lon in enumerate(lons):
        for j, lat in enumerate(lats[1:-1]):
            top[i,j] = norm(u_minus, v_minus, i, j)
            bottom[i,j] = norm(u_mean, v_mean, i, j)

    sigma = top/bottom - 2
    return sigma

### using files that are already at level 850 hPa
model = 'IPSL-CM6A-LR'
model = 'CESM2'
# model='CanESM5'
# model='HadGEM3-GC3-1MM'
box = 'ism1'
version = 'c'
for box in ['am3','wam4','ism1','easm2','am1']:
    for version in ['c','a']:

# vam = xr.open_dataset('/p/tmp/mayayami/vwnd.mon.mean.nc').vwnd.sel(level=850)
# uam = xr.open_dataset('/p/tmp/mayayami/uwnd.mon.mean.nc').uwnd.sel(level=850)
        if version=='c':
            slicesm = cslicesm
        elif version=='a':
            slicesm = aslicesm

        vam = xr.open_dataset('/p/tmp/mayayami/NAHosMIP/extra_boxes/{}_{}va_{}.nc'.format(model,version, box)).V.squeeze()[slicesm[model][0]:slicesm[model][1]]
        uam = xr.open_dataset('/p/tmp/mayayami/NAHosMIP/extra_boxes/{}_{}ua_{}.nc'.format(model,version, box)).U.squeeze()[slicesm[model][0]:slicesm[model][1]]

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

        v_seas = vam.groupby('time.month').mean(dim='time')
        u_seas = uam.groupby('time.month').mean(dim='time')

        v_mean = (v1+v7)/2
        u_mean = (u1+u7)/2

        Lo, La = u1.shape[0],u1.shape[1]

        sigma_mn = np.full((12,Lo,La),np.nan)

        for im in np.arange(0,12): 
            v_minus_t = v1 - v_seas[im]
            u_minus_t = u1 - u_seas[im]
            sigma_mn[im] = get_sigma(u_minus_t,v_minus_t,u_mean,v_mean)


        sigma_array = v_seas.copy(data=sigma_mn).rename('sigma')
        sigma_array.to_netcdf('DNS/{}_{}va_{}_seassigma.nc'.format(model,version, box))
        # sigma_array.to_netcdf('DNS/NCEPre_seassigma.nc')
