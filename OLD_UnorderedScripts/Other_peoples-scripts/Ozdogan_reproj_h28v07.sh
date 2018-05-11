#!/bin/sh

exec < tile.h28v07.txt 
while read nam
do
echo $nam
src=`gdalinfo $nam | grep NDVI | sed -n '4p' | cut -d"=" -f 2`
echo $src
nam2=`echo $nam | cut -d"." -f1-2`
#gdal_merge.py -n 0 -o $nam.tif -co "BIGTIFF=YES" $nam.h24v04.005.tif $nam.h24v05.005.tif 
gdalwarp -of GTiff -s_srs '+proj=sinu +a=6371007.181 +b=6371007.181 +unit=m' -t_srs 'EPSG:4326' -te 104.0 14.0 107.0 16.0 -r near "$src" $nam2.geo.lao.tif 
done


