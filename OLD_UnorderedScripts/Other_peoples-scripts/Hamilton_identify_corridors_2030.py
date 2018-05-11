# IMPORT SYSTEM MODULES
from __future__ import division
import sys, string, os, arcgisscripting, time, math

starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())

# CREATE THE GEOPROCESSOR OBJECT
print "CREATING GEOPROCESSOR OBJECT"
gp = arcgisscripting.create(9.3)

# ----- DEFINE INPUTS
workDir = "F:/DataF/chamilton/NWR_housing_2030/"

# loop through all NWR files, add field for corridor, calculate connection in corridor field
dirList = ["terra_reduced", "aqua_terra_reduced"]

#  Add corridor field to refuge or outside world
distList = ["1","5","10","25","50"]   # list furthest distance last !!!
for dir in dirList:
	for dist in distList:
		gp.workspace = workDir + dir + "/" + dist + "/"
		shps = gp.ListFeatureClasses()
		for shp in shps:
			print shp
			
			# Add corridor flag field
			print "gp= AddField -> CORRIDOR" 
			gp.AddField_management(shp,"CORRIDOR","LONG")
			
			# Calculate corridor
			rows = gp.UpdateCursor(shp)
			row = rows.next()
			while row:
				if dir == "terra_reduced":
					if row.DIST_PARK == 0 and row.DIST_OUT == 0 and row.TERRA == 1: 
						row.CORRIDOR = 1
					else:
						row.CORRIDOR = 0
				if dir == "aqua_terra_reduced":
					if row.DIST_PARK == 0 and row.DIST_OUT == 0 and row.TERRA_AQUA == 1: 
						row.CORRIDOR = 1
					else:
						row.CORRIDOR = 0						
						
					
				rows.UpdateRow(row)
				row = rows.next()

			
			# # Multipart to Singlepart
			# p = dir.find("_erase")
			# outdir = dir[0:p] + "_final/"
			# singleout = workDir + outdir + dist + "/" + shp[0:len(shp)-4] + "_corridors.shp"
			# print "gp= Multipart to Singlepart ->", singleout
			# gp.MultipartToSinglepart_management(shp,singleout)
			
			# # Add corridor flag field
			# p = dir.find("_reduced")
			# outdir = dir[0:p] + "_final/"
			# addout = workDir + outdir + dist + "/" + shp[0:len(shp)-12] + "_corridors.shp"
			# if not gp.Exists(addout):
				# print "gp= AddField -> AREA", addout
				# gp.AddField_management(shp,"AREA","DOUBLE")
			# else:
				# print addout, "already exists...skipping ADDFIELD"
			
			# # Calculate area for each polygon to compare 
			# print "gp= CalculateField -> AREA"
			# gp.CalculateField_management(addout, "AREA", "float(!shape.area!)", "PYTHON")
			# exit(0)
		
		
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())

print "start: " + starttime
print "end: " + endtime
	
