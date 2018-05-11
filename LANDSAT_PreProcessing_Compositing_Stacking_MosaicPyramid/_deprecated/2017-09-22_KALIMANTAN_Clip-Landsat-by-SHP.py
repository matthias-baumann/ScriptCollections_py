# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import gdal, ogr
import baumiTools as bt
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " +  starttime)
print("")
# ####################################### DRIVERS AND FOLDER-PATHS ############################################ #
inputFolder = "E:/Baumann/KALIMANTAN_Wilting/Landsat_TS/"
outputFolder = "E:/Baumann/KALIMANTAN_Wilting/Landsat_TS_clipped/"
extentShape = bt.baumiVT.CopyToMem("E:/Baumann/KALIMANTAN_Wilting/Extent.shp")
# ####################################### PROCESSING ########################################################## #
# (1) Get Folders that we want to process, start loop
folderList = bt.baumiFM.GetFilesInFolderWithEnding(inputFolder, "", fullPath = False)
for folder in folderList:


exit(0)

for file in fileList:
    print(file)
# Define full input and output-Path
    inPath = inputFolder + file
    outPath = outputFolder + file
    outPath = outPath.replace(".tif","_clip.tif")
# Do the clip
    outFile = bt.baumiRT.ClipRasterBySHP(extentShape, inPath)
# Write file to dist
    bt.baumiRT.CopyMEMtoDisk(outFile, outPath)
# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")