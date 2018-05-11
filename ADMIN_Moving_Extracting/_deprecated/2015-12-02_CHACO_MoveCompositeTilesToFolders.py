# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import os
import time
import datetime
import shutil
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ####################################### FOLDER PATHS AND FUNCTIONS ########################################## #
source_folder = "G:/CHACO/_COMPOSITING/ScratchData/"
def MoveFile(sourceFolder, ending, destFolder):
    fileList = os.listdir(sourceFolder)
    for file in fileList:
        if file.find(ending) >= 0 and file.find("dataCube") < 0:
            source = sourceFolder + file
            dest = destFolder + file
            shutil.move(source, dest)

def DeleteFile(sourceFolder, ending):
    fileList = os.listdir(sourceFolder)
    for file in fileList:
        if file.find(ending) >= 0:
            remove = sourceFolder + file
            os.remove(remove)

# (1) MOVE FILES
print("Imagery")
outFolder = "G:/CHACO/_COMPOSITING/_Composite_Landsat8_2015/DOY319_Nov15/"
MoveFile(source_folder, "PBC_multiYear_Imagery", outFolder)

print("Metrics")
outFolder = "G:/CHACO/_COMPOSITING/_Composite_Landsat8_2015/Metrics_Nov15/"
MoveFile(source_folder, "Metrics", outFolder)
#DeleteFile(source_folder, "Metrics")

print("Flags")
outFolder = "G:/CHACO/_COMPOSITING/_Composite_Landsat8_2015/DOY319_Nov15_MetaInfo/"
MoveFile(source_folder, "MetaFlags", outFolder)

print("Cubes")
#DeleteFile(source_folder, "dataCube")

# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #		
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")