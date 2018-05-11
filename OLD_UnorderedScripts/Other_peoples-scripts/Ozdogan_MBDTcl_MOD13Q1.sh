#!/bin/bash
# Bash script to download all modis hdf files for a particular year
# to the current directory.
#
# Beware this script will only download level 5 products
# if other products are selected the script will fail.
#
# Coded by Koen Hufkens at Boston University 2010

server="ftp://e4ftl01.cr.usgs.gov/"

# give a MODIS product, year and a tiles file containing
# a list of tiles to be downloaded
# e.g. ./MBDTcl.sh MCD43A4 2009 tiles.txt


# set product subdirectory name based upon product name
filename=`echo $1 | cut -c 1-3`
echo $filename

if [ "$filename" = "MOD" ]; then

subset="MOLT"

elif [ "$filename" = "MYD" ]; then

subset="MOLA"

elif [ "$filename" = "MCD" ]; then

subset="MOTA"

else
	echo "Not a MODIS product!"
	exit
fi


# set product name
product=$1

# set year
year=$2

# read tiles file
tiles=`cat $3`

echo "$server/$subset/$product.005/"

echo "#########################################################################"
ncftpls -l `echo "$server/$subset/$product.005/"` | awk '{print $NF}' | grep `echo $year` > doy.txt
doy=`cat doy.txt`
rm doy.txt
	
	for i in $doy
	do
	
		for j in $tiles
		do
	
		ncftpls -l `echo "$server/$subset/$product.005/$i/"` | awk '{print $NF}' | grep ".hdf" | grep $j | sed '/\.xml/d' > hdflist.txt
		hdflist=`cat hdflist.txt`
		rm hdflist.txt
		
			for k in $hdflist
			do
			
			echo "Downloading: $k"
			wget -q `echo "$server/$subset/$product.005/$i/$k"`
			
			done
		done
	done
echo "############################# DONE ######################################"

