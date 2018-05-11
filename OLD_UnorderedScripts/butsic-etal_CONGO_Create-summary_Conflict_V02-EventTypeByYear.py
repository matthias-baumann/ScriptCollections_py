 
 
 # SCRIPT ONLY RUNS WITH ARC 9.3 --> FOR SWITCH TO 10.1, PLEASE RE-CODE WITH THE ARCPY MODULE 

 
 
 
 #IMPORT SYSTEM MODULES
from __future__ import division
from math import sqrt
import sys, string, os, arcgisscripting
import time

starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())

# CREATE THE GEOPROCESSOR OBJECT
print("CREATING GEOPROCESSOR OBJECT")
gp = arcgisscripting.create(9.3)

print("")
print("---------------------------------------------------------------------------------------------")
# ASSIGN INPUTS AND OUTPUT VARIABLES
REGION_File = "X:/mbaumann/Congo/Process04_Create-Summary-Dataset/SummaryDataset_Secteur.shp"
CONFLICT_File = "X:/mbaumann/Congo/Process02_ConvertProjections-RasterizeData/DRC_ConflictData_Projected.shp"
outputFile = "X:/mbaumann/Congo/Process04_Create-Summary-Dataset/Conflict_Summary_Eventype_ByYear.csv"

# CREATE OUTPUT FILE TO WRITE TO
fout = open(outputFile, "w")
fout.write("REGION_ID,No_events_ALL,No_events_9000,No_events_0005,No_events_0510,ET_01_ALL,ET_01_9000,ET_01_0005,ET_01_0510,ET_02_ALL,ET_02_9000,ET_02_0005,ET_02_0510,ET_03_ALL,ET_03_9000,ET_03_0005,ET_03_0510,ET_04_ALL,ET_04_9000,ET_04_0005,ET_04_0510,ET_05_ALL,ET_05_9000,ET_05_0005,ET_05_0510,ET_06_ALL,ET_06_9000,ET_06_0005,ET_06_0510,ET_07_ALL,ET_07_9000,ET_07_0005,ET_07_0510,ET_08_ALL,ET_08_9000,ET_08_0005,ET_08_0510,ET_09_ALL,ET_09_9000,ET_09_0005,ET_09_0510,Fat_0_ALL,Fat_0_9000,Fat_0_0005,Fat_0_0510,Fat_01-10_ALL,Fat_01-10_9000,Fat_01-10_0005,Fat_01-10_0510,Fat_11-50_ALL,Fat_11-50_9000,Fat_11-50_0005,Fat_11-50_0510,Fat_51-100_ALL,Fat_51-100_9000,Fat_51-100_0005,Fat_51-100_0510,Fat_101-200_ALL,Fat_101-200_9000,Fat_101-200_0005,Fat_101-200_0510,Fat_201-500_ALL,Fat_201-500_9000,Fat_201-500_0005,Fat_201-500_0510,Fat_501-1000_ALL,Fat_501-1000_9000,Fat_501-1000_0005,Fat_501-1000_0510,Fat_1000_ALL,Fat_1000_9000,Fat_1000_0005,Fat_1000_0510\n")

# make a temporary feature layer for both layers
gp.MakeFeatureLayer_management(CONFLICT_File, "Conflict_layer")
gp.MakeFeatureLayer_management(REGION_File, "Region_layer")


# CREATE EMPTY LISTS TO STORE ALL POSSIBLE IDs
idList = []
typeID_List = []
interactCode_List = []


# POPULATE LISTS WITH REGION-IDs
rows = gp.SearchCursor("Region_layer")
row = rows.next()
while row:
	if row.ID not in idList:
		idList.append(row.ID)
	row = rows.next()
	
# POPULATE LISTS FROM CONFLICT-FILE	
rows = gp.SearchCursor("Conflict_layer")
row = rows.next()	
while row:
	if row.EVENT_TYPE not in typeID_List:
		typeID_List.append(row.EVENT_TYPE)
	if row.INTERACTIO not in interactCode_List:
		interactCode_List.append(row.INTERACTIO)
	row = rows.next()

for ID in idList:
	i = idList.index(ID)
	print("Sectuer-ID: " + str(ID))
	print("")
	# Number of events
	print("1. Number of events:")
	# Set variables initially to zero
	No_events_ALL = 0
	No_events_9000 = 0
	No_events_0005 = 0
	No_events_9510 = 0
	clause = "\"ID\" = " + str(ID)
	gp.SelectLayerByAttribute_management("Region_layer", "NEW_SELECTION", clause)
	gp.SelectLayerByLocation_management("Conflict_layer", "COMPLETELY_WITHIN", "Region_layer")
	result = gp.GetCount_management("Conflict_layer")
	No_events_ALL = int(result.GetOutput(0))
	print("Entire Period:" + str(No_events_ALL))
	PeriodClause = "\"Year\" < 2000" 
	gp.SelectLayerByAttribute_management("Conflict_layer", "SUBSET_SELECTION", PeriodClause)
	result = gp.GetCount_management("Conflict_layer")
	No_events_9000 = int(result.GetOutput(0))
	print("Period 1990-2000:" + str(No_events_9000))
	PeriodClause = "\"Year\" >= 2000 AND \"Year\" < 2005"

	gp.SelectLayerByLocation_management("Conflict_layer", "COMPLETELY_WITHIN", "Region_layer")
	gp.SelectLayerByAttribute_management("Conflict_layer", "SUBSET_SELECTION", PeriodClause)
	result = gp.GetCount_management("Conflict_layer")
	No_events_0005 = int(result.GetOutput(0))
	print("Period 2000-2005:" + str(No_events_0005))
	PeriodClause = "\"Year\" >= 2005 AND \"Year\" < 2011"

	gp.SelectLayerByLocation_management("Conflict_layer", "COMPLETELY_WITHIN", "Region_layer")
	gp.SelectLayerByAttribute_management("Conflict_layer", "SUBSET_SELECTION", PeriodClause)
	result = gp.GetCount_management("Conflict_layer")
	No_events_0510 = int(result.GetOutput(0))
	print("Period 2005-2010:" + str(No_events_0510))
	
	print("")
	# Number of events by event-type
	print("2. Number of events by EVENT_TYPE:")
	for type in typeID_List:
		#Reset the outputvariables
		events_ALL = 0
		events_9000 = 0
		events_0005 = 0
		events_0510 = 0
		print("--> " + type)
		typeClause = "\"EVENT_TYPE\" = '" + str(type) + "'"

		gp.SelectLayerByLocation_management("Conflict_layer", "COMPLETELY_WITHIN", "Region_layer")
		gp.SelectLayerByAttribute_management("Conflict_layer", "SUBSET_SELECTION", typeClause)
		result = gp.GetCount_management("Conflict_layer")
		events_ALL = int(result.GetOutput(0))
		print("Entire Period:" + str(events_ALL))
		PeriodClause = "\"Year\" < 2000" 
		gp.SelectLayerByLocation_management("Conflict_layer", "COMPLETELY_WITHIN", "Region_layer")
		gp.SelectLayerByAttribute_management("Conflict_layer", "SUBSET_SELECTION", typeClause)
		gp.SelectLayerByAttribute_management("Conflict_layer", "SUBSET_SELECTION", PeriodClause)
		result = gp.GetCount_management("Conflict_layer")
		events_9000 = int(result.GetOutput(0))
		print("Period 1990-2000:" + str(events_9000))
		PeriodClause = "\"Year\" >= 2000 AND \"Year\" < 2005"
		gp.SelectLayerByLocation_management("Conflict_layer", "COMPLETELY_WITHIN", "Region_layer")
		gp.SelectLayerByAttribute_management("Conflict_layer", "SUBSET_SELECTION", typeClause)
		gp.SelectLayerByAttribute_management("Conflict_layer", "SUBSET_SELECTION", PeriodClause)
		result = gp.GetCount_management("Conflict_layer")
		events_0005 = int(result.GetOutput(0))
		print("Period 2000-2005:" + str(events_0005))
		PeriodClause = "\"Year\" >= 2005 AND \"Year\" < 2011"
		gp.SelectLayerByLocation_management("Conflict_layer", "COMPLETELY_WITHIN", "Region_layer")
		gp.SelectLayerByAttribute_management("Conflict_layer", "SUBSET_SELECTION", typeClause)
		gp.SelectLayerByAttribute_management("Conflict_layer", "SUBSET_SELECTION", PeriodClause)
		result = gp.GetCount_management("Conflict_layer")
		events_0510 = int(result.GetOutput(0))
		print("Period 2005-2010:" + str(events_0510))
		# Write into variables for output
		if type == "Battle-No change of territory":
			type01_all = events_ALL
			type01_9000 = events_9000
			type01_0005 = events_0005
			type01_0510 = events_0510
		if type == "Battle-Government regains territory":
			type02_all = events_ALL
			type02_9000 = events_9000
			type02_0005 = events_0005
			type02_0510 = events_0510
		if type == "Battle-Rebels overtake territory":
			type03_all = events_ALL
			type03_9000 = events_9000
			type03_0005 = events_0005
			type03_0510 = events_0510
		if type == "Non-violent activity by a conflict actor":
			type04_all = events_ALL
			type04_9000 = events_9000
			type04_0005 = events_0005
			type04_0510 = events_0510
		if type == "Riots/Protests":
			type05_all = events_ALL
			type05_9000 = events_9000
			type05_0005 = events_0005
			type05_0510 = events_0510
		if type == "Violence against civilians":
			type06_all = events_ALL
			type06_9000 = events_9000
			type06_0005 = events_0005
			type06_0510 = events_0510
		if type == "Rioters (DRC)":
			type07_all = events_ALL
			type07_9000 = events_9000
			type07_0005 = events_0005
			type07_0510 = events_0510
		if type == "Non-violent transfer of territory":
			type08_all = events_ALL
			type08_9000 = events_9000
			type08_0005 = events_0005
			type08_0510 = events_0510
		if type == "Headquarters or base established":
			type09_all = events_ALL
			type09_9000 = events_9000
			type09_0005 = events_0005
			type09_0510 = events_0510
	print("")
	
	print("3. Summarize by caterories of fatalities:")
	# Set output-variables to zero
	cat_00_all = 0
	cat_00_9000 = 0
	cat_00_0005 = 0
	cat_00_0510 = 0
	cat_01_10_all = 0
	cat_01_10_9000 = 0
	cat_01_10_0005 = 0
	cat_01_10_0510 = 0
	cat_11_50_all = 0
	cat_11_50_9000 = 0
	cat_11_50_0005 = 0
	cat_11_50_0510 = 0
	cat_51_100_all = 0
	cat_51_100_9000 = 0
	cat_51_100_0005 = 0
	cat_51_100_0510 = 0	
	cat_101_200_all = 0
	cat_101_200_9000 = 0
	cat_101_200_0005 = 0
	cat_101_200_0510 = 0	
	cat_201_500_all = 0
	cat_201_500_9000 = 0
	cat_201_500_0005 = 0
	cat_201_500_0510 = 0
	cat_501_1000_all = 0
	cat_501_1000_9000 = 0
	cat_501_1000_0005 = 0
	cat_501_1000_0510 = 0
	cat_1000_all = 0
	cat_1000_9000 = 0
	cat_1000_0005 = 0
	cat_1000_0510 = 0

	gp.SelectLayerByLocation_management("Conflict_layer", "COMPLETELY_WITHIN", "Region_layer")
	rows_fat = gp.SearchCursor("Conflict_layer")
	row_fat = rows_fat.next()
	while row_fat:
		if row_fat.TOTAL_FATA == 0:
			cat_00_all = cat_00_all + 1
		if row_fat.TOTAL_FATA >= 1 and row_fat.TOTAL_FATA <= 10:
			cat_01_10_all = cat_01_10_all + 1
		if row_fat.TOTAL_FATA >= 11 and row_fat.TOTAL_FATA <= 50:
			cat_11_50_all = cat_11_50_all + 1
		if row_fat.TOTAL_FATA >= 51 and row_fat.TOTAL_FATA <= 100:
			cat_51_100_all = cat_51_100_all + 1
		if row_fat.TOTAL_FATA >= 101 and row_fat.TOTAL_FATA <= 200:
			cat_101_200_all = cat_101_200_all + 1
		if row_fat.TOTAL_FATA >= 201 and row_fat.TOTAL_FATA <= 500:
			cat_201_500_all = cat_201_500_all + 1
		if row_fat.TOTAL_FATA >= 501 and row_fat.TOTAL_FATA <= 1000:
			cat_501_1000_all = cat_501_1000_all + 1
		if row_fat.TOTAL_FATA >= 1001:
			cat_1000_all = cat_1000_all + 1	
		row_fat = rows_fat.next()
	print("--> Entire Period")
	print("Fatalities = 0: " + str(cat_00_all))
	print("Fatalities = 1-10: " + str(cat_01_10_all))
	print("Fatalities = 11-50: " + str(cat_11_50_all))
	print("Fatalities = 51-100: " + str(cat_51_100_all))
	print("Fatalities = 101-200: " + str(cat_101_200_all))
	print("Fatalities = 201-500: " + str(cat_201_500_all))
	print("Fatalities = 501-1000: " + str(cat_501_1000_all))
	print("Fatalities > 1000: " + str(cat_1000_all))

	PeriodClause = "\"Year\" < 2000"
	gp.SelectLayerByLocation_management("Conflict_layer", "COMPLETELY_WITHIN", "Region_layer")	
	gp.SelectLayerByAttribute_management("Conflict_layer", "SUBSET_SELECTION", PeriodClause)
	rows_fat = gp.SearchCursor("Conflict_layer")
	row_fat = rows_fat.next()
	while row_fat:
		if row_fat.TOTAL_FATA == 0:
			cat_00_9000 = cat_00_9000 + 1
		if row_fat.TOTAL_FATA >= 1 and row_fat.TOTAL_FATA <= 10:
			cat_01_10_9000 = cat_01_10_9000 + 1
		if row_fat.TOTAL_FATA >= 11 and row_fat.TOTAL_FATA <= 50:
			cat_11_50_9000 = cat_11_50_9000 + 1
		if row_fat.TOTAL_FATA >= 51 and row_fat.TOTAL_FATA <= 100:
			cat_51_100_9000 = cat_51_100_9000 + 1
		if row_fat.TOTAL_FATA >= 101 and row_fat.TOTAL_FATA <= 200:
			cat_101_200_9000 = cat_101_200_9000 + 1
		if row_fat.TOTAL_FATA >= 201 and row_fat.TOTAL_FATA <= 500:
			cat_201_500_9000 = cat_201_500_9000 + 1
		if row_fat.TOTAL_FATA >= 501 and row_fat.TOTAL_FATA <= 1000:
			cat_501_1000_9000 = cat_501_1000_9000 + 1
		if row_fat.TOTAL_FATA >= 1001:
			cat_1000_9000 = cat_1000_9000 + 1	
		row_fat = rows_fat.next()
	print("--> Period 1990 - 2000")
	print("Fatalities = 0: " + str(cat_00_9000))
	print("Fatalities = 1-10: " + str(cat_01_10_9000))
	print("Fatalities = 11-50: " + str(cat_11_50_9000))
	print("Fatalities = 51-100: " + str(cat_51_100_9000))
	print("Fatalities = 101-200: " + str(cat_101_200_9000))
	print("Fatalities = 201-500: " + str(cat_201_500_9000))
	print("Fatalities = 501-1000: " + str(cat_501_1000_9000))
	print("Fatalities > 1000: " + str(cat_1000_9000))

	PeriodClause = "\"Year\" >= 2000 AND \"Year\" < 2005"
	gp.SelectLayerByLocation_management("Conflict_layer", "COMPLETELY_WITHIN", "Region_layer")
	gp.SelectLayerByAttribute_management("Conflict_layer", "SUBSET_SELECTION", PeriodClause)
	rows_fat = gp.SearchCursor("Conflict_layer")
	row_fat = rows_fat.next()
	while row_fat:
		if row_fat.TOTAL_FATA == 0:
			cat_00_0005 = cat_00_0005 + 1
		if row_fat.TOTAL_FATA >= 1 and row_fat.TOTAL_FATA <= 10:
			cat_01_10_0005 = cat_01_10_0005 + 1
		if row_fat.TOTAL_FATA >= 11 and row_fat.TOTAL_FATA <= 50:
			cat_11_50_0005 = cat_11_50_0005 + 1
		if row_fat.TOTAL_FATA >= 51 and row_fat.TOTAL_FATA <= 100:
			cat_51_100_0005 = cat_51_100_0005 + 1
		if row_fat.TOTAL_FATA >= 101 and row_fat.TOTAL_FATA <= 200:
			cat_101_200_0005 = cat_101_200_0005 + 1
		if row_fat.TOTAL_FATA >= 201 and row_fat.TOTAL_FATA <= 500:
			cat_201_500_0005 = cat_201_500_0005 + 1
		if row_fat.TOTAL_FATA >= 501 and row_fat.TOTAL_FATA <= 1000:
			cat_501_1000_0005 = cat_501_1000_0005 + 1
		if row_fat.TOTAL_FATA >= 1001:
			cat_1000_0005 = cat_1000_0005 + 1	
		row_fat = rows_fat.next()
	print("--> Period 2000 - 2005")
	print("Fatalities = 0: " + str(cat_00_0005))
	print("Fatalities = 1-10: " + str(cat_01_10_0005))
	print("Fatalities = 11-50: " + str(cat_11_50_0005))
	print("Fatalities = 51-100: " + str(cat_51_100_0005))
	print("Fatalities = 101-200: " + str(cat_101_200_0005))
	print("Fatalities = 201-500: " + str(cat_201_500_0005))
	print("Fatalities = 501-1000: " + str(cat_501_1000_0005))
	print("Fatalities > 1000: " + str(cat_1000_0005))

	PeriodClause = "\"Year\" >= 2005 AND \"Year\" < 2011"
	gp.SelectLayerByLocation_management("Conflict_layer", "COMPLETELY_WITHIN", "Region_layer")
	gp.SelectLayerByAttribute_management("Conflict_layer", "SUBSET_SELECTION", PeriodClause)
	rows_fat = gp.SearchCursor("Conflict_layer")
	row_fat = rows_fat.next()
	while row_fat:
		if row_fat.TOTAL_FATA == 0:
			cat_00_0510 = cat_00_0510 + 1
		if row_fat.TOTAL_FATA >= 1 and row_fat.TOTAL_FATA <= 10:
			cat_01_10_0510 = cat_01_10_0510 + 1
		if row_fat.TOTAL_FATA >= 11 and row_fat.TOTAL_FATA <= 50:
			cat_11_50_0510 = cat_11_50_0510 + 1
		if row_fat.TOTAL_FATA >= 51 and row_fat.TOTAL_FATA <= 100:
			cat_51_100_0510 = cat_51_100_0510 + 1
		if row_fat.TOTAL_FATA >= 101 and row_fat.TOTAL_FATA <= 200:
			cat_101_200_0510 = cat_101_200_0510 + 1
		if row_fat.TOTAL_FATA >= 201 and row_fat.TOTAL_FATA <= 500:
			cat_201_500_0510 = cat_201_500_0510 + 1
		if row_fat.TOTAL_FATA >= 501 and row_fat.TOTAL_FATA <= 1000:
			cat_501_1000_0510 = cat_501_1000_0510 + 1
		if row_fat.TOTAL_FATA >= 1001:
			cat_1000_0510 = cat_1000_0510 + 1	
		row_fat = rows_fat.next()
	print("--> Period 2005 - 2010")
	print("Fatalities = 0: " + str(cat_00_0510))
	print("Fatalities = 1-10: " + str(cat_01_10_0510))
	print("Fatalities = 11-50: " + str(cat_11_50_0510))
	print("Fatalities = 51-100: " + str(cat_51_100_0510))
	print("Fatalities = 101-200: " + str(cat_101_200_0510))
	print("Fatalities = 201-500: " + str(cat_201_500_0510))
	print("Fatalities = 501-1000: " + str(cat_501_1000_0510))
	print("Fatalities > 1000: " + str(cat_1000_0510))
	print("")
	print("---------------------------------------------------------------------------------------------")
	print("")
	
	# WRITE OUTPUT TO FILE
	fout.write(str(ID)
	+ "," + str(No_events_ALL) + "," + str(No_events_9000) + "," + str(No_events_0005) + "," + str(No_events_0510)
	+ "," + str(type01_all) + "," + str(type01_9000) + "," + str(type01_0005) + "," + str(type01_0510)
	+ "," + str(type02_all) + "," + str(type02_9000) + "," + str(type02_0005) + "," + str(type02_0510)
	+ "," + str(type03_all) + "," + str(type03_9000) + "," + str(type03_0005) + "," + str(type03_0510)
	+ "," + str(type04_all) + "," + str(type04_9000) + "," + str(type04_0005) + "," + str(type04_0510)
	+ "," + str(type05_all) + "," + str(type05_9000) + "," + str(type05_0005) + "," + str(type05_0510)
	+ "," + str(type06_all) + "," + str(type06_9000) + "," + str(type06_0005) + "," + str(type06_0510)
	+ "," + str(type07_all) + "," + str(type07_9000) + "," + str(type07_0005) + "," + str(type07_0510)
	+ "," + str(type08_all) + "," + str(type08_9000) + "," + str(type08_0005) + "," + str(type08_0510)
	+ "," + str(type09_all) + "," + str(type09_9000) + "," + str(type09_0005) + "," + str(type09_0510)
	+ "," + str(cat_00_all) + "," + str(cat_00_9000) + "," + str(cat_00_0005) + "," + str(cat_00_0510)
	+ "," + str(cat_01_10_all) + "," + str(cat_01_10_9000) + "," + str(cat_01_10_0005) + "," + str(cat_01_10_0510)
	+ "," + str(cat_11_50_all) + "," + str(cat_11_50_9000) + "," + str(cat_11_50_0005) + "," + str(cat_11_50_0510)
	+ "," + str(cat_51_100_all) + "," + str(cat_51_100_9000) + "," + str(cat_51_100_0005) + "," + str(cat_51_100_0510)
	+ "," + str(cat_101_200_all) + "," + str(cat_101_200_9000) + "," + str(cat_101_200_0005) + "," + str(cat_101_200_0510)
	+ "," + str(cat_201_500_all) + "," + str(cat_201_500_9000) + "," + str(cat_201_500_0005) + "," + str(cat_201_500_0510)
	+ "," + str(cat_501_1000_all) + "," + str(cat_501_1000_9000) + "," + str(cat_501_1000_0005) + "," + str(cat_501_1000_0510)
	+ "," + str(cat_1000_all) + "," + str(cat_1000_9000) + "," + str(cat_1000_0005) + "," + str(cat_1000_0510)
	+ "\n") 
		
		
fout.close()

endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())

print("start: " + starttime)
print("end: " + endtime)
