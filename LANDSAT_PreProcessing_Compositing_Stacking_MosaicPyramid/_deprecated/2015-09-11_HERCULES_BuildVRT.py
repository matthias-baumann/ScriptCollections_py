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
root_folder = "G:/HERCULES/02_Compositing/"
target = "2010_Fall_DOY280"
# #### (1) BUILD OUTPUT TEXT FILES WITH PATHS FROM THE DIFFERENT FOLDERS
print("Build List")
finalFileList = []
# (A) FROM EU MAIN TERRITORY
part = "Rest"
searchfolder = root_folder + part + "/" + target + "/"
file_list = os.listdir(searchfolder)
for file in file_list:
    if file.find(".bsq") >= 0:
        filepath = searchfolder + file
        finalFileList.append(filepath)
# (B) CYPRUS
part = "Cyprus"
searchfolder = root_folder + part + "/" + target + "/"
file_list = os.listdir(searchfolder)
for file in file_list:
    if file.find(".bsq") >= 0:
        filepath = searchfolder + file
        finalFileList.append(filepath)

# #### (2)  WRITE LIST TO OUTPUT-FILE
outfile = root_folder + target + "_VRT-Filelist.txt"
f_open = open(outfile, "w")
for item in finalFileList:
    f_open.write(item + "\n")
f_open.close()

# #### (3) BUILD VRT
print("Build VRT")
outVRT = root_folder + target + "_VRT.vrt"
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