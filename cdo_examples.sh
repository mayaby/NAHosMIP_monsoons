#!/bin/bash

""" This is a list of EXAMPLES of cdo commands used to process the files. You would have to adapt the lines to your files."""

## get boxes
cdo -sellonlatbox,285,317.5,-15,-5 file.nc file_box.nc

## zonal mean
cdo -L -zonmean file.nc file_zmean.nc

## change precipitation units
cdo -mulc,86400 -setattribute,pr@units=mm/day ifile.nc ofile.nc

## regrid files to a new grid
cdo remapcon,grid.txt ifile.nc ofile.nc

## create seamask
cdo -f nc2 setctomiss,0 -gtc,0 -remapcon,ifile.nc -topo seamask.nc

## apply seamask
cdo mul ifile.nc seamask.nc ofile.nc

## other used functions: 
cdo mergetime
cdo timmean
cdo yearmean


