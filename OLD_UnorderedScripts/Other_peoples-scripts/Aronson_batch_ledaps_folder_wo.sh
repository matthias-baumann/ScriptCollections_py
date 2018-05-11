#!/bin/sh

mydir=`pwd`
for tmp in `find . -maxdepth 1 -type d`
do
	cd $mydir
        cd $tmp
	echo "Wechsel in $tmp"
	for datei in lndsr.*.hdf
	do
		if [ -f $datei ]
		then 
		  echo "was already processed!"
		else 
		  /bin/csh /bin/do_ledaps.csh *_WO.txt
		fi 
	done
done
