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
root_folder = "G:/CHACO/_ANALYSES/LandUseChange_1985-2000-2013/Run12_Tiles/"
target = "Metrics_Nov15"
# #### (1) BUILD OUTPUT TEXT FILES WITH PATHS FROM THE DIFFERENT FOLDERS
print("Build List")
finalFileList = []
# (A) FROM EU MAIN TERRITORY
searchfolder = root_folder + "/"# + target + "/"
file_list = os.listdir(searchfolder)
for file in file_list:
    if file.find(".bsq") >= 0:
        filepath = searchfolder + file
        finalFileList.append(filepath)

# #### (2)  WRITE LIST TO OUTPUT-FILE
#outfile = root_folder + target + "_VRT-Filelist.txt"
outfile = "G:/CHACO/_ANALYSES/LandUseChange_1985-2000-2013/fileList.txt"
f_open = open(outfile, "w")
for item in finalFileList:
    f_open.write(item + "\n")
f_open.close()

# #### (3) BUILD VRT
print("Build VRT")
#outVRT = root_folder + target + "_VRT.vrt"
outVRT = "G:/CHACO/_ANALYSES/LandUseChange_1985-2000-2013/baumann_etal_2017_ChacoPlus_LCC_allClasses_85_00_13.vrt"
command =  "gdalbuildvrt.exe -input_file_list " + outfile + " " + outVRT
os.system(command)

# #### (4) CALCULATE PYRAMIDS FOR THE VRT-FILE
print("Calculate Pyramids")
command = "gdaladdo.exe " + outVRT + " 2 4 8 16 32 64"
os.system(command)



# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")