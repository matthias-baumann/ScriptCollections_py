# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import os
import time, datetime
import shutil
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" + starttime)
print("")
# ####################################### FOLDER PATHS ######################################################## #
LEDAPSoutgoing = "G:/LEDAPS/outgoing/"
LEDAPSincoming = "G:/LEDAPS/incoming/"
LandsatRAW = "G:/MISSIONES/Landsat/"
# ####################################### START PROCESSING #################################################### #
# (1) DELETE ERATIC SCENES
# Build list
errorTXT = "G:/MISSIONES/00_PreProcessing/ReOrder_FileCheck_v03_delete.txt"
deleteList = []
file_open = open(errorTXT, "r")
for line in file_open:
	FP = line[3:6] + "_" + line[6:9]
	combo = [FP, line[:-1]]
	deleteList.append(combo)
file_open.close()
# Delete according to list
for combo in deleteList:
	path = LEDAPSoutgoing + combo[0] + "/" + combo[1] + "/"
	print(combo[1] + " (" + str((deleteList.index(combo))+1) + " of " + str(len(deleteList)) + ")")
	try:
		shutil.rmtree(path)
	except:
		print("Error. Check Manually!")
print("Done deleting files, copy now scenes to re-process")
# (2) COPY SCENES TO REPROCESS
reprocessTXT = "G:/MISSIONES/00_PreProcessing/ReOrder_FileCheck_v03_reprocess.txt"
# Build List
copyList = []
file_open = open(reprocessTXT, "r")
for line in file_open:
    scene = line[:-1]
    copyList.append(scene)
file_open.close()
# Copy scenes according to list
for scene in copyList:
    print(scene + " (" + str((copyList.index(scene)) + 1) + " of " + str(len(copyList)) + ")")
    sourcePath = LandsatRAW + scene + ".tar.gz"
    destPath = LEDAPSincoming + scene + ".tar.gz"
    if not os.path.exists(destPath) and os.path.exists(sourcePath):
        shutil.copy(sourcePath, destPath)
    else:
        print("--> File not existent anymore")

# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")