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
outFile = "D:/Matthias/Projects-and-Publications/Projects_Collaborating_Active/PICTO_Chaco/Scenes/p1984-1990.txt"
xml = "D:/Matthias/Projects-and-Publications/Projects_Collaborating_Active/PICTO_Chaco/Scenes/metadata.xml"
cutoff = 1984
pathrows = [227078, 227079, 228077, 228078, 228079, 229077, 229078, 230077, 230078]
sensors = ["LT5", "LE7"]
# #### (1) BUILD OUTPUT TEXT FILES WITH PATHS FROM THE DIFFERENT FOLDERS
finalFileList = []
L45open = open(xml, "r")
for line in L45open:
    if line.find("sceneID") >= 0:
        p1 = line.find(">")
        p2 = line.rfind("<")
        sceneID = line[p1+1:p2]
        sensor = sceneID[0:3]
        year = int(sceneID[9:13])
        pr = int(sceneID[3:9])
        if year >= cutoff and year < 1990 and pr in pathrows and sensor in sensors:
            finalFileList.append(sceneID)


print(len(finalFileList))

out = open (outFile, "w")

for sceneID in finalFileList:
    out.write(sceneID + "\n")
out.close()



# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")