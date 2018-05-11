#!/bin/sh

exec < hdf.list 
while read nam
do
echo $nam
nam2=`echo $nam | cut -d"." -f1-4`
dd=`gdalinfo $nam.hdf | grep "NDVI" | sed -n '4p' | cut -d"=" -f2`
gdal_translate -of Gtiff "$dd" $nam2.NDVI.tif
rm -rf *.xml
done


