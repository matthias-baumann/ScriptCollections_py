# IMPORT SYSTEM MODULES
from __future__ import division
import sys, string, os, arcgisscripting, time, math

if len(sys.argv) < 4:
	print "Usage: near_outside_world.py <a_or_t> <refuge_name> <buffer_distance>"

starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())

# CREATE THE GEOPROCESSOR OBJECT
print "CREATING GEOPROCESSOR OBJECT"
gp = arcgisscripting.create(9.3)

# Set the necessary product code
gp.SetProduct("ArcInfo")

# Load required toolboxes...
gp.AddToolbox("C:/Program Files (x86)/ArcGIS/ArcToolbox/Toolboxes/Analysis Tools.tbx")

# command line parameters
a_or_t = sys.argv[1]
refuge = sys.argv[2]
buffdis = sys.argv[3]


# Switch used to turn on processing loop (pick up where we left off)
switch = 0


# ----- DEFINE INPUTS
workDir = "F:/dataF/chamilton/NWR_housing_2030/"
worldFile = workDir + "us_pbg00_dissolve.shp"
eraseDir = workDir + "buffers_02/"

# loop through all buffers, erase from world file and calculate near distance to edge of buffer
dirList = ["aqua_terra_reduced"] #, "aqua_terra_reduced_08b"]
#outList = ["terra_near_07a", "aqua_terra_near_07b"]

bufferList = ["25"] #"5","10","25","50"]
for dir in dirList:
	i = dirList.index(dir)
#	outdir = outList[i]
	for buffer in bufferList:
		bufferDir = workDir + dir + "/" + buffer + "/"
#		outputDir = workDir + outdir + "/" + buffer + "/" 

		gp.workspace = bufferDir
		shpfiles = gp.ListFeatureClasses()
		for shp in shpfiles:
			
			# flip on switch if arguments match
			if shp.find(refuge) >= 0 and buffer == buffdis and dir[0] == a_or_t: switch = 1
			
			if switch == 1:
				print shp
			
				# BUG FIX - delete NEAR_DIST field if it already exists (returns erroneous results if field already exists)
				fields = gp.ListFields(shp)
				for field in fields:
					if field.name == "NEAR_DIST":
						print "gp= DELETE FIELD ->", field.name
						gp.DeleteField_management(shp,"NEAR_DIST")
					if field.name == "DIST_OUT": 
						print "gp= DELETE FIELD ->", field.name
						gp.DeleteField_management(shp,"DIST_OUT")
			
				eraseout = workDir + "buffer_erase_25a.shp"
				p = shp.find("_buff")
				eraseshp = eraseDir + buffer + "/" + shp[0:p] + "_buff" + buffer + "km.shp"
				print "gp= ERASE ->", eraseout 
				gp.Erase_analysis(worldFile,eraseshp,eraseout)
			
				# calculate near features to outside world from buffer polygons
				print "gp= NEAR -> OUTSIDE WORLD", buffer, "km buffer"
				distance = (int(buffer) + 1) * 1000
				gp.Near_analysis(shp, eraseout, distance)
				
				# transfer distance values to new field
				print "gp= AddField -> DIST_OUT" 
				gp.AddField_management(shp,"DIST_OUT","DOUBLE")
				rows = gp.UpdateCursor(shp)
				str(buffer)
				row = rows.next()
				while row:
					row.DIST_OUT = row.NEAR_DIST
					rows.UpdateRow(row)
					row = rows.next()
				del row
				del rows
				
				
				# calculate near features to refuge boundary from buffer polygons
				# p = shp.find("_buff")
				# refuge = shp[0:p]
				# refugeShp = workDir + "NWRs_01/" + refuge + ".shp"
				
				# print "gp= NEAR -> REFUGE BOUNDARY"
				# input = bufferDir + shp
				# gp.Near_analysis(input, refugeShp, "", "NO_LOCATION", "NO_ANGLE")
				
					
				
				# BUG FIX - delete NEAR_DIST field if it already exists (returns erroneous results if field already exists)
				fields = gp.ListFields(shp)
				for field in fields:
					if field.name == "NEAR_DIST":
						print "gp= DELETE FIELD ->", field.name
						gp.DeleteField_management(shp,"NEAR_DIST")
			
				
				gp.Delete_management(eraseout)
			
			
			
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())

print "start: " + starttime
print "end: " + endtime
