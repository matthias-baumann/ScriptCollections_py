# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import os
import time
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " +  starttime)
print("")
# ####################################### DRIVERS AND FOLDER-PATHS ############################################ #
iF = "G:/CHACO/ReprojectedScenes/S1_extracted_new/"
oF_vv = "G:/CHACO/ReprojectedScenes/VV/"
oF_vh = "G:/CHACO/ReprojectedScenes/VH/"
# ####################################### FUNCTIONS ########################################################### #
scenes = [iF + file + "/" + file + ".SAFE" for file in os.listdir(iF)]
for scene in scenes:
    print(scene)
    p = scene.rfind("/")
    output_vv = oF_vv + scene[p+1:]
    output_vv = output_vv.replace(".SAFE", ".tif")
    output_vh = output_vv
    output_vh = output_vh.replace("/VV/", "/VH/")
    command_vh = "gdal_translate -b 1 -q " + scene + " " + output_vh
    command_vv = "gdal_translate -b 2 -q " + scene + " " + output_vv
    os.system(command_vh)
    os.system(command_vv)
# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")