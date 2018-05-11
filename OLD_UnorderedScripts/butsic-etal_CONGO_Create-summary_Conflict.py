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
print("")
print("---------------------------------------------------------------------------------------------")
# ASSIGN INPUTS AND OUTPUT VARIABLES
REGION_File = "X:/mbaumann/Congo/Process04_Create-Summary-Dataset/SummaryDataset_Secteur.shp"
CONFLICT_File = "X:/mbaumann/Congo/Process02_ConvertProjections-RasterizeData/DRC_ConflictData_Projected.shp"
outputFile = "X:/mbaumann/Congo/Process04_Create-Summary-Dataset/Conflict_Summary.csv"

# CREATE OUTPUT FILE TO WRITE TO
fout = open(outputFile, "w")
fout.write("REGION_ID,No_events,ET_01,ET_02,ET_03,ET_04,ET_05,ET_06,ET_07,ET_08,ET_09,IC_12,IC_23,IC_24,IC_26,IC_22,IC_25,IC_38,IC_44,IC_13,IC_14,IC_27,IC_17,IC_47,IC_37,IC_78,IC_57,IC_34,IC_28,IC_11,IC_33,IC_48,IC_16,IC_15,IC_18,IC_68,IC_58,IC_36,IC_55,IC_45,IC_20,IC_40,IC_30,IC_10,IC_80,IC_60,IC_50,Fat_0,Fat_01-10,Fat_11-50,Fat_51-100,Fat_101-200,Fat_201-500,Fat_501-1000,Fat_1000\n")

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
	print "Sectuer-ID: " + str(ID)
	print("")
	# Number of events
	print("1. Number of events:")
	clause = "\"ID\" = " + str(ID)
	gp.SelectLayerByAttribute_management("Region_layer", "NEW_SELECTION", clause)
	gp.SelectLayerByLocation_management("Conflict_layer", "COMPLETELY_WITHIN", "Region_layer")
	result = gp.GetCount_management("Conflict_layer")
	No_events = int(result.GetOutput(0))
	print(No_events)
	print("")
	
	# Number of events by event-type
	print("2. Number of events by EVENT_TYPE:")
	for type in typeID_List:
		typeClause = "\"EVENT_TYPE\" = '" + str(type) + "'"
		gp.SelectLayerByLocation_management("Conflict_layer", "COMPLETELY_WITHIN", "Region_layer")
		gp.SelectLayerByAttribute_management("Conflict_layer", "SUBSET_SELECTION", typeClause)
		result = gp.GetCount_management("Conflict_layer")
		event_count = int(result.GetOutput(0))
		print(type + ": " + str(event_count))
		if type == "Battle-No change of territory":
			type01 = event_count
		if type == "Battle-Government regains territory":
			type02 = event_count
		if type == "Battle-Rebels overtake territory":
			type03 = event_count
		if type == "Non-violent activity by a conflict actor":
			type04 = event_count
		if type == "Riots/Protests":
			type05 = event_count
		if type == "Violence against civilians":
			type06 = event_count
		if type == "Rioters (DRC)":
			type07 = event_count
		if type == "Non-violent transfer of territory":
			type08 = event_count
		if type == "Headquarters or base established":
			type09 = event_count
	print("")
	
	print("3. Number of events by INTERACTION_CODE:")
	for code in interactCode_List:
		codeClause = "\"INTERACTIO\" = " + str(code)
		gp.SelectLayerByLocation_management("Conflict_layer", "COMPLETELY_WITHIN", "Region_layer")
		gp.SelectLayerByAttribute_management("Conflict_layer", "SUBSET_SELECTION", codeClause)
		result = gp.GetCount_management("Conflict_layer")
		event_count = int(result.GetOutput(0))
		print(str(code) + ": " + str(event_count))
		if code == 12:
			code12 = event_count
		if code == 23:
			code23 = event_count
		if code == 24:
			code24 = event_count
		if code == 26:
			code26 = event_count
		if code == 22:
			code22 = event_count
		if code == 25:
			code25 = event_count
		if code == 38:
			code38 = event_count
		if code == 44:
			code44 = event_count
		if code == 13:
			code13 = event_count
		if code == 14:
			code14 = event_count
		if code == 27:
			code27 = event_count
		if code == 17:
			code17 = event_count
		if code == 47:
			code47 = event_count
		if code == 37:
			code37 = event_count	
		if code == 78:
			code78 = event_count
		if code == 57:
			code57 = event_count
		if code == 34:
			code34 = event_count
		if code == 28:
			code28 = event_count
		if code == 11:
			code11 = event_count
		if code == 33:
			code33 = event_count
		if code == 48:
			code48 = event_count
		if code == 16:
			code16 = event_count
		if code == 15:
			code15 = event_count
		if code == 18:
			code18 = event_count
		if code == 68:
			code68 = event_count
		if code == 58:
			code58 = event_count
		if code == 36:
			code36 = event_count
		if code == 55:
			code55 = event_count
		if code == 45:
			code45 = event_count	
		if code == 20:
			code20 = event_count
		if code == 40:
			code40 = event_count
		if code == 30:
			code30 = event_count
		if code == 10:
			code10 = event_count
		if code == 80:
			code80 = event_count	
		if code == 60:
			code60 = event_count
		if code == 50:
			code50 = event_count
	print("")
	
	print("4. Summarize by caterories of fatalities:")
	cat_00 = 0
	cat_01_10 = 0
	cat_11_50 = 0
	cat_51_100 = 0
	cat_101_200 = 0
	cat_201_500 = 0
	cat_501_1000 = 0
	cat_1000 = 0
	gp.SelectLayerByLocation_management("Conflict_layer", "COMPLETELY_WITHIN", "Region_layer")
	rows_fat = gp.SearchCursor("Conflict_layer")
	row_fat = rows_fat.next()
	while row_fat:
		if row_fat.TOTAL_FATA == 0:
			cat_00 = cat_00 + 1
		if row_fat.TOTAL_FATA >= 1 and row_fat.TOTAL_FATA <= 10:
			cat_01_10 = cat_01_10 + 1
		if row_fat.TOTAL_FATA >= 11 and row_fat.TOTAL_FATA <= 50:
			cat_11_50 = cat_11_50 + 1
		if row_fat.TOTAL_FATA >= 51 and row_fat.TOTAL_FATA <= 100:
			cat_51_100 = cat_51_100 + 1
		if row_fat.TOTAL_FATA >= 101 and row_fat.TOTAL_FATA <= 200:
			cat_101_200 = cat_101_200 + 1
		if row_fat.TOTAL_FATA >= 201 and row_fat.TOTAL_FATA <= 500:
			cat_201_500 = cat_201_500 + 1
		if row_fat.TOTAL_FATA >= 501 and row_fat.TOTAL_FATA <= 1000:
			cat_501_1000 = cat_501_1000 + 1
		if row_fat.TOTAL_FATA >= 1001:
			cat_1000 = cat_1000 + 1
	
		row_fat = rows_fat.next()
	print("Fatalities = 0: " + str(cat_00))
	print("Fatalities = 1-10: " + str(cat_01_10))
	print("Fatalities = 11-50: " + str(cat_11_50))
	print("Fatalities = 51-100: " + str(cat_51_100))
	print("Fatalities = 101-200: " + str(cat_101_200))
	print("Fatalities = 201-500: " + str(cat_201_500))
	print("Fatalities = 501-1000: " + str(cat_501_1000))
	print("Fatalities > 1000: " + str(cat_1000))
	print("")
	print("---------------------------------------------------------------------------------------------")
	print("")
	
	# WRITE OUTPUT TO FILE
	fout.write(str(ID) + "," + str(No_events) + "," + str(type01) + "," + str(type02) + "," + str(type03) + "," + str(type04) + "," + str(type05) + "," + str(type06) + "," + str(type07) + "," + str(type08) + "," + str(type09)
	+ "," + str(code12)+ "," + str(code23)+ "," + str(code24) + "," + str(code26) + "," + str(code22) + "," + str(code25) + "," + str(code38) + "," + str(code44) + "," + str(code13) + "," + str(code14)
	+ "," + str(code27) + "," + str(code17) + "," + str(code47) + "," + str(code37) + "," + str(code78) + "," + str(code57) + "," + str(code34) + "," + str(code28) + "," + str(code11) + "," + str(code33)
	+ "," + str(code48) + "," + str(code16) + "," + str(code15) + "," + str(code18) + "," + str(code68)
	+ "," + str(code58) + "," + str(code36) + "," + str(code55) + "," + str(code45) + "," + str(code20)
	+ "," + str(code40) + "," + str(code30) + "," + str(code10) + "," + str(code80) + "," + str(code60) + "," + str(code50)
	+ "," + str(cat_00) + "," + str(cat_01_10) + "," + str(cat_11_50) + "," + str(cat_51_100) + "," + str(cat_101_200) + "," + str(cat_201_500) + "," + str(cat_501_1000) + "," + str(cat_1000)
	+ "\n") 
		
		
fout.close()

endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())

print "start: " + starttime
print "end: " + endtime
