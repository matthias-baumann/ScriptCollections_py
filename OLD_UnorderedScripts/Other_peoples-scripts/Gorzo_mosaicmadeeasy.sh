#!/bin/bash
# this is a script to turn your pile of raw, downloaded modis files into mosaics
# this script is written to run this in the folder where you downloaded your files. just place in that folder and run it!

#this makes a list of all the days you downloaded data for
listofmodisdays=`ls *.hdf | cut -d. -f2 | uniq`

for i in $listofmodisdays #for each date...
do
#this lists all the tiles for that date, which will be mosaicked together into one cohesive image
	ls *$i*.hdf > tiles$i
#change path for wherever your modis tools are
	/data/gorzo/MRT/bin/mrtmosaic -i tiles$i -o mosaic$i.hdf
done
