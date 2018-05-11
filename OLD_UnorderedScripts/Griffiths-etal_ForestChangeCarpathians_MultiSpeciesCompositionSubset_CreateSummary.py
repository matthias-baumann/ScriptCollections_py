

 #IMPORT SYSTEM MODULES
from __future__ import division
import sys, string, os
import time

# SET STARTING TIME
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())

# DEFINE INPUT FILE MANUALLY
input = "E:/tempdata/mbaumann/Carpathian_AccuracyAssessment/DataProcessing/Romania_RAW-data.txt"
output = "E:/tempdata/mbaumann/Carpathian_AccuracyAssessment/DataProcessing/Romania_ExtractedInformation_fromPython.txt"

# BUILD LISTS
RAW_List = []
IDList = []
SP1_T_List = []
SP2_T_List = []
SP3_T_List = []
SP4_T_List = []
SP1_P_List = []
SP2_P_List = []
SP3_P_List = []
SP4_P_List = []


# NOW OPEN THE TXT-FILE, THAT WE FORMATTED ACCORDINGLY
infoFile = open(input, "r")

# LOOP THROUGH EACH LINE AND EXTRACT INFORMATION
for line in infoFile:
	RAW_List.append(line)
	# (1) Go for the id-entry
	pos_right = line.find("&")
	id = line[0:pos_right]
	IDList.append(id)
	print("Processing ID:", id)
	id = id + "&_" # this is to find the index of the other information we want to extract
	line = line.replace(id,"")

	# (2a) Go for the first species proportion
	pos_right = line.find("_")
	SP1_P = line[0:pos_right]
	SP1_P_List.append(SP1_P)
	line = "&" + line
	SP1_P = "&" + SP1_P + "_"
	line = line.replace(SP1_P,"")

	# (2b) Go for the first species type
	pos_right = line.find("_")
	SP1_T = line[0:pos_right]
	SP1_T_List.append(SP1_T)
	line = "&" + line
	SP1_T = "&" + SP1_T + "_"
	line = line.replace(SP1_T,"")

	# (3a) Go for the second species proportion
	if line.find("&") < 0:
		pos_right = line.find("_")
		SP2_P = line[0:pos_right]
		SP2_P_List.append(SP2_P)
		line = "&" + line
		SP2_P = "&" + SP2_P + "_"
		line = line.replace(SP2_P,"")
	else:
		SP2_P_List.append("NN")

	# (3b) Go for the second species type
	if line.find("&") < 0:
		pos_right = line.find("_")
		SP2_T = line[0:pos_right]
		SP2_T_List.append(SP2_T)
		line = "&" + line
		SP2_T = "&" + SP2_T + "_"
		line = line.replace(SP2_T,"")
	else:
		SP2_T_List.append("NN")
		
	# (4a) Go for the third species proportion
	if line.find("&") < 0:
		pos_right = line.find("_")
		SP3_P = line[0:pos_right]
		SP3_P_List.append(SP3_P)
		line = "&" + line
		SP3_P = "&" + SP3_P + "_"
		line = line.replace(SP3_P,"")
	else:
		SP3_P_List.append("NN")
		
	# (4b) Go for the third species type
	if line.find("&") < 0:
		pos_right = line.find("_")
		SP3_T = line[0:pos_right]
		SP3_T_List.append(SP3_T)
		line = "&" + line
		SP3_T = "&" + SP3_T + "_"
		line = line.replace(SP3_T,"")	
	else:
		SP3_T_List.append("NN")
	
	# (5a) Go for the fourth species proportion
	if line.find("&") < 0:
		pos_right = line.find("_")
		SP4_P = line[0:pos_right]
		SP4_P_List.append(SP4_P)
		line = "&" + line
		SP4_P = "&" + SP4_P + "_"
		line = line.replace(SP4_P,"")
	else:
		SP4_P_List.append("NN")
	
	# (5b) Go for the fourth species type
	if line.find("&") < 0:
		pos_right = line.find("_")
		SP4_T = line[0:pos_right]
		SP4_T_List.append(SP4_T)
		line = "&" + line
		SP4_T = "&" + SP4_T + "_"
		line = line.replace(SP4_T,"")	
	else:
		SP4_T_List.append("NN")
	

print("")
# WRITE LISTS INTO CSV-FILE
print("Write Output-file...")
out = open (output, "w")
out.write("ID SP1_T SP1_P SP2_T SP2_P SP3_T SP3_P SP4_T SP4_P\n")
for ID in IDList:
	i = IDList.index(ID)		# this returns the current element index of the first list - use to grab same element in other lists
	out.write(ID + " " + SP1_T_List[i] + " " + SP1_P_List[i] + " " + SP2_T_List[i] + " " + SP2_P_List[i] + " " + SP3_T_List[i] + " " + SP3_P_List[i] + " " + SP4_T_List[i] + " " + SP4_P_List[i] + "\n")
out.close()
print("")


endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())

print("start: ", starttime)
print("end: ", endtime)
print("")

