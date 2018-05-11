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
source_folder = "G:/HERCULES/02_Compositing/02_CompositingTiles/"
def MoveFile(sourceFolder, ending, destFolder):
    fileList = os.listdir(sourceFolder)
    for file in fileList:
        if file.find(ending) >= 0 and file.find("dataCube") < 0:
            source = sourceFolder + file
            dest = destFolder + file
            shutil.move(source, dest)

# (1) MOVE FILES
print("Move Imagery")
outFolder = "G:/HERCULES/02_Compositing/Rest/2000_Spring_DOY95/"
MoveFile(source_folder, "Imagery", outFolder)

print("Move Metrics")
outFolder = "G:/HERCULES/02_Compositing/Rest/2000_Metrics/"
MoveFile(source_folder, "Metrics", outFolder)

print("Move Flags")
outFolder = "G:/HERCULES/02_Compositing/Rest/2000_MetaFlags/"
MoveFile(source_folder, "MetaFlags", outFolder)


# (2) DELETE  REMAINING FILES
print("Delete Remaining Files")
fileList = os.listdir(source_folder)
for file in fileList:
    delete = source_folder + file
    os.remove(delete)


# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #		
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")