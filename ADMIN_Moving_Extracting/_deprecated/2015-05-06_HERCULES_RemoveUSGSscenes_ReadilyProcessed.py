# THIS SCRIPT WAS WRITTEN, BECAUSE WE NEEDED SPACE ON THE NAS-DRIVE.
# THUS, ALL SCENES THAT WERE RETURNED WITHOUT AN ERROR AFTER THE IDL-SCRIPT, ARE BEING REMOVED.

# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import os
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ####################################### FUNCTIONS, FOLDER PATHS AND BASIC VARIABLES ######################### #
scenes_done = "G:/HERCULES/01_PreProcessing/01_Reports/InputInfos_HERCULES_2010_Batch03_20150506_correctScenes.txt"
RAW_folder = "G:/LEDAPS/HERCULES_LandsatRAW/2010/"
# ####################################### PROCESSING ########################################################## #
# (1) OPEN EMPTY-TILE-LIST-FILE, THEN COPY THE FILES
f_open = open(scenes_done, "r")
for scene in f_open:
    print(scene[:-1])
    deletePath = RAW_folder + scene[:-1] + ".tar.gz"
    try:
        os.remove(deletePath)
    except:
        print("Error, check manually...")
f_open.close()

# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")
