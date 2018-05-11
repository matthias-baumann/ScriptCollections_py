# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import os
import time
import baumiTools as bt
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ####################################### FUNCTIONS, FOLDER PATHS AND BASIC VARIABLES ######################### #
jobList = ["hansen_year_loss"]
for job in jobList:
    print(job)
    tiles_folder = "Z:/_SHARED_DATA/PLTEMP/" + job + "/"
    outVRT = "Z:/_SHARED_DATA/PLTEMP/" + job + "/" + job + ".vrt"
    outTXT = "Z:/_SHARED_DATA/PLTEMP/" + job + "_fileList.txt"
    # #### (1) BUILD OUTPUT TEXT FILES WITH PATHS FROM THE DIFFERENT FOLDERS
    print("Build List")
    finalFileList = []
    # #### (A) FROM EU MAIN TERRITORY
    file_list = os.listdir(tiles_folder)
    for file in file_list:
        if file.endswith(".tif"):
            filepath = tiles_folder + file
            finalFileList.append(filepath)
    # #### (2)  WRITE LIST TO OUTPUT-FILE
    f_open = open(outTXT, "w")
    for item in finalFileList:
        f_open.write(item + "\n")
    f_open.close()
    # #### (3) BUILD VRT
    print("Build VRT")
    command =  "gdalbuildvrt.exe -overwrite -srcnodata 0 -input_file_list " + outTXT + " " + outVRT
    os.system(command)
    # # #### (5) BUILD PYRAMID
    print("Calculate Pyramids, vrt")
    command = "gdaladdo.exe " + outVRT + " 2 4 8 16 32 64"
    #os.system(command)
    os.remove(outTXT)

# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")