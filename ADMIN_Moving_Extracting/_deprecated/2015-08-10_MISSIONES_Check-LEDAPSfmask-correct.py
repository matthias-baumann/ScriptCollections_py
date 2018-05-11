# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import os
import time
from ZumbaTools.FileManagement_Tools import *
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ####################################### FUNCTIONS, FOLDER PATHS AND BASIC VARIABLES ######################### #
root_folder = "G:/LEDAPS/outgoing/"

processSuccess = [] # all files correctly processed and available
processDelete = [] # all scenes in which one condition was not met --> no GCP|mtl|fmask|ledaps (in that order)
processReprocess = [] # all scenes with only error in LEDAPS or fmask

# Loop through footprint
FP_folder = [(root_folder + s + "/") for s in os.listdir(root_folder)]
for FP in FP_folder:
    print(FP)
    scenes = [(FP + scene + "/") for scene in os.listdir(FP)]
# Loop through scene
    for scene in scenes:
        eval = [scene[27:-1],[]]
# Check if GCP is available
        GCP_yn = GetFilesInFolderWithEnding(scene, "GCP.txt")
        gcp_ok = 0
        if len(GCP_yn) == 1:
            gcp_ok = 1
        eval[1].append(gcp_ok)
# Check if MTL is available
        MTL_yn = GetFilesInFolderWithEnding(scene, "MTL.txt")
        mtl_ok = 0
        if len(MTL_yn) == 1:
            mtl_ok = 1
        eval[1].append(mtl_ok)
# Check if Fmask is available and GE 25MB
        Fmask_yn = GetFilesInFolderWithEnding(scene, ".c3s3p10.bsq")
        fmask_ok = 0
        if len(Fmask_yn) == 1:
            Fmask_size_MB = os.path.getsize(Fmask_yn[0]) / 1000000
            if Fmask_size_MB >= 25:
                fmask_ok = 1
        eval[1].append(fmask_ok)
# Check if LEDAPS file is present and GE 700MB
        ledaps_yn = [(scene + file) for file in os.listdir(scene) if file.find('lndsr.') >= 0 and file.endswith(".hdf")]
        ledaps_ok = 0
        if len(ledaps_yn) == 1:
            ledaps_size_MB = os.path.getsize(ledaps_yn[0]) / 1000000
            if ledaps_size_MB >= 500:
                ledaps_ok = 1
        eval[1].append(ledaps_ok)
# Evaluate the eval and assign to list
        if sum(eval[1]) == 4:
            processSuccess.append(eval[0])
        else:
            processDelete.append(eval[0])
            if eval[1][0] == 1 and eval[1][1] == 1:
                processReprocess.append(eval[0])


# Write Lists to files
WriteListToTXT(processSuccess,"G:/MISSIONES/00_PreProcessing/ReOrder_FileCheck_v03_success.txt")
WriteListToTXT(processDelete,"G:/MISSIONES/00_PreProcessing/ReOrder_FileCheck_v03_delete.txt")
WriteListToTXT(processReprocess,"G:/MISSIONES/00_PreProcessing/ReOrder_FileCheck_v03_reprocess.txt")

# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")