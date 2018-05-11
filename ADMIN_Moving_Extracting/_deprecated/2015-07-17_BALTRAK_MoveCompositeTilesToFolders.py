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
source_folder = "H:/Baltrak/02_Compositing_NEW/02_CompositingTiles/"
def MoveFile(sourceFolder, ending, destFolder):
    fileList = os.listdir(sourceFolder)
    for file in fileList:
        if file.find(ending) >= 0 and file.find("dataCube") < 0:
            source = sourceFolder + file
            dest = destFolder + file
            shutil.move(source, dest)

# (1) MOVE FILES
print("Move Imagery")
outFolder = "H:/Baltrak/02_Compositing_NEW/2000_Fall_DOY260/"
MoveFile(source_folder, "Imagery", outFolder)

print("Move Metrics")
outFolder = "H:/Baltrak/02_Compositing_NEW/2000_Metrics/"
MoveFile(source_folder, "Metrics", outFolder)

print("Move Flags")
outFolder = "H:/Baltrak/02_Compositing_NEW/2000_Flags/"
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