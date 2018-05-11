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
inputFolder = "X:/BFAST/Scene1 2nd try/evi_masked/"
outputFolder = "X:/BFAST/Scene1 2nd try/evi_masked/_Clipped/"
extentShape = bt.baumiVT.CopyToMem("X:/BFAST/Scene1 2nd try/evi_masked/Extent.shp")
# ####################################### PROCESSING ########################################################## #
# (1) Get Files that we want to process, start loop
fileList = bt.baumiFM.GetFilesInFolderWithEnding(inputFolder, ".tif", fullPath = False)
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