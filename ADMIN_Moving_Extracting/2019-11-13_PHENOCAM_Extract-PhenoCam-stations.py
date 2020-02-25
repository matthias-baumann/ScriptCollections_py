# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import os
import time
import shutil
import re
import baumiTools as bt
import json
from tqdm import tqdm
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ####################################### FOLDER PATHS AND FUNCTIONS ########################################## #
root_folder = 'D:/_TEACHING/__Classes-Modules_HUB/MSc-M1_Quantitative-Methods/WS_2019-2020/Data/PhenoCam/'
outfile = root_folder + "PhenoCam_sites_ALL.csv"

fileList = bt.baumiFM.GetFilesInFolderWithEnding(root_folder + "PhenoCam_V2_1674/data/", "_meta.json", fullPath=True)
values = [["ID", "Lat", "Lon", "sitename_short", "sitename_long"]]
idCount = 1

coordCheck = []

for file in tqdm(fileList):
    with open(file, 'r') as f:
        array = json.load(f)
        try:
            phenoInfo = array.get('phenocam_site')
            if not [round(phenoInfo.get('lat'),3), round(phenoInfo.get('lon'), 3)] in coordCheck:
                vals = [idCount, phenoInfo.get('lat'), phenoInfo.get('lon'), phenoInfo.get('sitename'), phenoInfo.get('long_name')]
                values.append(vals)
                idCount += 1
                coordCheck.append([round(phenoInfo.get('lat'),3), round(phenoInfo.get('lon'),3)])
        except:
            pass

bt.baumiFM.WriteListToCSV(outfile, values, ",")

# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #		
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")