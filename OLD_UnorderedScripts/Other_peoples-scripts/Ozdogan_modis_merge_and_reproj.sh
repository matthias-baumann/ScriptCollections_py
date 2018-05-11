#!/bin/sh

exec < tiffs.txt 
while read nam
do
echo $nam
#nam2=`echo $nam | cut -d"." -f1-4`
gdal_merge.py -n 0 -o $nam.tif -co "BIGTIFF=YES" $nam.h24v04.005.tif $nam.h24v05.005.tif 
gdalwarp -of GTiff -s_srs '+proj=sinu +a=6371007.181 +b=6371007.181 +unit=m' -t_srs 'EPSG:4326' -te 74.0 35.0 100.0 44.0 $nam.tif -co "BIGTIFF=YES" -r near $nam.geo.tif 
done


