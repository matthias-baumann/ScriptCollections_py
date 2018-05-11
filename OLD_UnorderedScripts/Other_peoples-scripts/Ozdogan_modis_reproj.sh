#!/bin/sh

while read date
do
echo $date

gdal_merge.py -o tmp.tif -of GTiff MOD13Q1.$date.h20v02.005.NDVI.tif MOD13Q1.$date.h20v03.005.NDVI.tif

gdalwarp -of GTiff -s_srs '+proj=sinu +a=6371007.181 +b=6371007.181 +units=m' -t_srs '+proj=utm +zone=37 +datum=WGS84' -tr 240 240 tmp.tif tmp2.tif

gdal_translate -of ENVI tmp2.tif MOD13Q1.$date.geo.NDVI.bsq

rm -f tmp.* tmp2.*

done

#exec < tiffs.txt 
#while read nam
#do
#echo $nam
#nam2=`echo $nam | cut -d"." -f1-4`
#gdalwarp -of GTiff -t_srs '+proj=utm +zone=13 +datum=WGS84' -tr 30 30 -te 376905.000 4091175.000 474765.000 4199385.000 $nam $nam2.utm.tif 
#done


