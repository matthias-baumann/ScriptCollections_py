# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import os
import time
import datetime
import gdal
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ####################################### FUNCTIONS, FOLDER PATHS AND BASIC VARIABLES ######################### #
root_folder = "G:/Baumann/_ANALYSES/LandUseChange_1985-2000-2015_UpdateWithRadar/Classification/Run_03/Tiles/"
outVRT = "G:/Baumann/_ANALYSES/LandUseChange_1985-2000-2015_UpdateWithRadar/Classification/Run_03/Run03_VRT.vrt"
outTXT = "G:/Baumann/_ANALYSES/LandUseChange_1985-2000-2015_UpdateWithRadar/Classification/Run_03/Run03_TXT.txt"
# #### (1) BUILD OUTPUT TEXT FILES WITH PATHS FROM THE DIFFERENT FOLDERS
print("Build List")
finalFileList = []
file_list = os.listdir(root_folder)
for file in file_list:
    if file.endswith(".tif"):
        filepath = root_folder + file
        finalFileList.append(filepath)
# #### (2)  WRITE LIST TO OUTPUT-FILE
f_open = open(outTXT, "w")
for item in finalFileList:
    f_open.write(item + "\n")
f_open.close()
# #### (3) BUILD VRT
print("Build VRT")
#outVRT = root_folder + target + "_VRT.vrt"
command =  "gdalbuildvrt.exe -input_file_list " + outTXT + " " + outVRT
os.system(command)

print("Calculate Pyramids, vrt")
command = "gdaladdo.exe " + outVRT + " 2 4 8 16 32 64"
os.system(command)
os.remove(outTXT)

# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")