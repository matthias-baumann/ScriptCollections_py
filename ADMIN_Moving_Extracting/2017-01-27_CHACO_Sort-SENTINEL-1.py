# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import os
import time
import shutil
import re
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ####################################### FOLDER PATHS AND FUNCTIONS ########################################## #
source_folder = "G:/CHACO/_COMPOSITING/Sentinel1_Data/_VV/"
matchFolder = "G:/CHACO/_COMPOSITING/Sentinel1_Data/"
outFolders = [folder for folder in os.listdir(matchFolder) if folder < "_VH" and folder < "_VV"]

fileList = [file for file in os.listdir(source_folder)]
for f in fileList:
    print(f)
    fSub = f[14:-9]
    fSub = fSub.replace("-", "_")
    #print(fSub)
    for of in outFolders:
        ofSub = of[17:-5]
        if re.search(fSub, ofSub, re.IGNORECASE):
            inFile = source_folder + f
            outFile = matchFolder + of + "/" + of + ".SAFE/measurement/" + f
            shutil.move(inFile, outFile)



# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #		
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")