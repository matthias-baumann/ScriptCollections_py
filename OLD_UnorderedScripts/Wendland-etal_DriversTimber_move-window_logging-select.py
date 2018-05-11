 #IMPORT SYSTEM MODULES
from __future__ import division
from math import sqrt
import sys, string, os, arcgisscripting
import time

starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())

# CREATE THE GEOPROCESSOR OBJECT
print "CREATING GEOPROCESSOR OBJECT"
gp = arcgisscripting.create(9.3)
# print "CHECKING OUT SPATIAL ANALYST EXTENSION"
# gp.CheckOutExtension("Spatial")

# ASSIGN INPUTS AND OUTPUT VARIABLES
loggingFile = "F:/DataF/kwendland/gistrials/GP_change/Logging-sites_GCS-WGS84.shp"
landsatFile = "F:/DataF/kwendland/gistrials/GP_change/Landsat_scenes/Landsat_select.shp"
outputFile = "F:/DataF/kwendland/gistrials/GP_change/Landsat_scenes/landsat-logging.csv"

# CREATE OUTPUT FILE TO WRITE TO
fout = open(outputFile, "w")
fout.write("MAJOR_LS,LS_N,LS_E,LS_S,LS_W,LOGSITES_NUM,LOGSITES_AREAM2,LOGSITES_AREAHA\n")


startrow = 10
endrow = 22
startpath = 165
endpath = 192

# make a temporary feature layer of landsat select for selections
gp.MakeFeatureLayer_management(landsatFile, "landsat_layer")
gp.MakeFeatureLayer_management(loggingFile, "logging_layer")

for r in range(startrow,endrow):
	for p in range(startpath,endpath):
	
		# SET AREA TOTALS TO ZERO
		aream2_sum = 0
		areaha_sum = 0
	
		# SELECT CURRENT PATH ROW FROM LANDSAT FILE
		clause = "\"pathrow\" = '" + str(p) + str(r) + "'"
		gp.SelectLayerByAttribute_management("landsat_layer", "NEW_SELECTION", clause)
		
		# MAKE SURE PATH ROW EXISTS 
		result = gp.GetCount_management("landsat_layer")
		count = int(result.GetOutput(0))
		
		# IF PATH ROW EXISTS THEN SELECT SURROUNDING 4 SCENES
		if count > 0:
			clause = "(path = " + str(p) + " - 1 AND row = " + str(r) + ") OR (path = " + str(p) + " + 1 AND row = " + str(r) + ") OR (path = " + str(p) + " AND row = " + str(r) + " - 1) OR (path = " + str(p) + " AND row = " + str(r) + " + 1)"
				
			gp.SelectLayerByAttribute_management("landsat_layer", "ADD_TO_SELECTION", clause)
			
			# GET NUMBER OF SELECTED LANDSAT SCENES
			result = gp.GetCount_management("landsat_layer")
			count = int(result.GetOutput(0))
			print p, r, count
			
			# IF ALL 4 SCENES EXIST THEN GET NUMBER OF SITES AND AREA 
			if count == 5:

				# SELECT LOGGING SITES USING SELECTED LANDSAT SCENES
				gp.SelectLayerByLocation_management("logging_layer", "COMPLETELY_WITHIN", "landsat_layer")
						
				# GET NUMBER OF LOGGING SITES
				result = gp.GetCount_management("logging_layer")
				site_count = int(result.GetOutput(0))	
				
				# GET SUM OF LOGGING AREA
				rows = gp.SearchCursor("logging_layer")
				row = rows.next()
				while row:				
					aream2_sum = aream2_sum + row.Area_m2
					areaha_sum = areaha_sum + row.Area_ha
					row = rows.next()
				
				
				# WRITE OUTPUT TO FILE
				fout.write(str(p) + str(r) + ",") 
				fout.write(str(p) + str(r-1) + "," + str(p-1) + str(r) + ",")
				fout.write(str(p) + str(r+1) + "," + str(p+1) + str(r) + ",")
				fout.write('%i' % site_count + "," + '%.2f' % aream2_sum + "," + '%.2f' % areaha_sum + "\n")
				

fout.close()

endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())

print "start: " + starttime
print "end: " + endtime
