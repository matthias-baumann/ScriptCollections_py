# ### BEGIN OF HEADER INFROMATION AND LOADING OF MODULES (Not all modules are actually required for the analysis) #######################
# IMPORT SYSTEM MODULES
import sys
import os
import time
import datetime

# ##### SET TIME-COUNT AND HARD-CODED FOLDER-PATHS #####
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("")
print("Starting process, time:", starttime)

pathRow = sys.argv[1]
source_folder = "E:\\kirkdata\\mbaumann\\Landsat_Processing\\Landsat\\" + pathRow + "\\"
# ##### START THE DELETING #####

folderList = os.listdir(source_folder)
for folder in folderList[:]:
	sceneFolder = source_folder + folder
	fileList = os.listdir(sceneFolder)
	for file in fileList[:]:
		if file.find("lndsr.") >= 0:
			removepath = sceneFolder + "\\" + file
			os.remove(removepath)


print("--------------------------------------------------------")
print("")

endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: ", starttime)
print("end: ", endtime)
print("")