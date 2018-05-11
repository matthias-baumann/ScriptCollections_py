# IMPORT SYSTEM MODULES
from __future__ import division
import sys, string, os, arcgisscripting, time, math

starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())

# CREATE THE GEOPROCESSOR OBJECT
print "CREATING GEOPROCESSOR OBJECT"
gp = arcgisscripting.create(9.3)

workDir = "F:/dataF/chamilton/NWR_housing_2030/terra_final/"

dirList = ["extra"]

for dir in dirList:
	gp.worskpace = workDir + dir + "/"
	mergeList = ""
	shps = gp.ListFeatureClasses()
	for shp in shps:
		outdir = workDir + "merged/"
		mergeout = workdir + outdir + shp[0:len(shp)-4] + "_merged.shp"
		mergeList = mergeList + shp + "; "
		
	mergeList = mergeList.strip("; ")

	gp.Merge_management(mergeList,mergeout)
	
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())

print "start: " + starttime
print "end: " + endtime
	

