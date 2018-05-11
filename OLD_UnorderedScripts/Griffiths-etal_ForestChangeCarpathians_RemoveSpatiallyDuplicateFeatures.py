

# LOAD SYSTEM MODULES
print("-------------------------------------------------------")
print("")
print("Load system modules")
import arcpy
import os
import time

#SET TIME-COUNT AND HARD-CODED FOLDER-PATHS #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("")
print("Starting process, time: " + starttime)
print("")

# DEFINE INPUT AND OUTPUT-LAYER
input = "E:/tempdata/mbaumann/Carpathian_AccuracyAssessment/DataProcessing/Slovakia_Edited_shpFile.shp"
output = "E:/tempdata/mbaumann/Carpathian_AccuracyAssessment/DataProcessing/Slovakia_Edited_shpFile_RemovedDuplicates.shp"

# LOAD SHP-FILES INTO MEMORY AND CREATE FEATURE-LAYER
print("Creating feature layers...")
arcpy.MakeFeatureLayer_management(input, "input_lyr")
arcpy.MakeFeatureLayer_management(output, "comparison_lyr")
print("")

# GET NUMBER OF ROWS IN THE SHP-FILE --> CASES TO BE PROCESSED
print("Getting Number of rows from shp-file...")
row_count = arcpy.GetCount_management(input)
print(row_count)
print("")

# SET ROW-COUNT TO ZERO, MAKE IT AS A STRING
counter = 0
counter_str = str(counter)

# INITIALIZE WHILE-LOOP
while counter < row_count:
	query = "\"FID\" = " + counter_str
	print("Working on query: " + query)
	# Process: Select Layer By Attribute...
	arcpy.SelectLayerByAttribute_management("input_lyr", "NEW_SELECTION", query)
	# Process: Select Layer By Location...
	arcpy.SelectLayerByLocation_management("comparison_lyr", "ARE_IDENTICAL_TO", "input_lyr", "", "NEW_SELECTION")
	# Process: Select Layer By Attribute (2)...
	arcpy.SelectLayerByAttribute_management("comparison_lyr", "REMOVE_FROM_SELECTION", query)
	# Process: Delete Features...
	arcpy.DeleteFeatures_management("comparison_lyr")	
	
	# Increase counter by one and make a string out of it
	counter = counter + 1
	counter_str = str(counter)
	

endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")