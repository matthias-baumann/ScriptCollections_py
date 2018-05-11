# IMPORT SYSTEM MODULES
from __future__ import division
import sys, string, os, arcgisscripting, time, math

starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())

# CREATE THE GEOPROCESSOR OBJECT
print "CREATING GEOPROCESSOR OBJECT"
gp = arcgisscripting.create(9.3)

workDir = "F:/DataF/chamilton/NWR_housing_2030/"
outputDir = workDir + "hdens_table/"
bufferDir = workDir + "output/pa_buffers/"
boundFile = workDir + "FWSInterest/NWRs_alb_Dissolve.shp"

# OPEN MASTER OUTPUT FILE AND WRITE HEADER
outFile1 = outputDir + "NWR_terra_all_buffers_HU_1940-2030.csv"
outFile2 = outputDir + "NWR_aqua_terra_all_buffers_HU_1940-2030.csv"
fout = open(outFile, "w")
fout.write("NWR_NAME,AREA,BUFFER_DIST,HU1940,HU1950,HU1960,HU1970,HU1980,HU1990,HU2000,HU2010,HU2020,HU2030\n")

gp.Workspace = bufferDir
fcList = gp.ListFeatureClasses("*NWR*")

for fc in fcList:

	print fc

	# GET PA NAME AND BUFFER DISTANCE FOR OUTPUT
	p1 = fc.find("NATIONAL")
	pa_name = fc[4:p1-1]
	pa_name = pa_name.replace("INTE", "")
	p2 = fc.find("km")
	p3 = fc.rfind("albers")
	bufferdist = fc[p3+7:p2]
	
	
	# RECALCULATE AREA OF EVERY POLYGON
	print "gp= CALCULATE FIELD [AREA] ->", fc
	gp.CalculateField_management(fc, "AREA", "float(!SHAPE.AREA!)", "PYTHON")
	
	# OPEN ATTRIBUTE output AND SUM HOUSING UNITS FOR EACH DECADE AND WRITE TO MASTER FILE
	area_sum = 0
	huList = [0,0,0,0,0,0,0,0,0,0]
	
	print "Summing Housing Units by Decade..."
	rows = gp.SearchCursor(fc)
	row = rows.next()
	while row:
	
		if row.WATER00 < 1:
		
			area_km = row.AREA / 1000000
			area_sum = area_sum + area_km
			
			# CALC HU BY DECADE
			hu40 = row.HDEN40 * area_km
			hu50 = row.HDEN50 * area_km
			hu60 = row.HDEN60 * area_km
			hu70 = row.HDEN70 * area_km
			hu80 = row.HDEN80 * area_km
			hu90 = row.HDEN90 * area_km
			hu00 = row.HDEN00 * area_km
			hu10 = row.HDEN10 * area_km
			hu20 = row.HDEN20 * area_km
			hu30 = row.HDEN30 * area_km
			
			# UPDATE HU SUM LIST
			huList[0] = huList[0] + hu40
			huList[1] = huList[1] + hu50
			huList[2] = huList[2] + hu60
			huList[3] = huList[3] + hu70
			huList[4] = huList[4] + hu80
			huList[5] = huList[5] + hu90
			huList[6] = huList[6] + hu00
			huList[7] = huList[7] + hu10
			huList[8] = huList[8] + hu20
			huList[9] = huList[9] + hu30
		
		row = rows.next()
	
	print "Writing output..."
	fout.write(pa_name + "," + '%.2f' % area_sum + "," + bufferdist + ",")
	for hu in huList:
		fout.write('%i' % hu + ",")	
	fout.write("\n")


# CLOSE OUTPUT
fout.close()	

endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())

print "start: " + starttime
print "end: " + endtime
