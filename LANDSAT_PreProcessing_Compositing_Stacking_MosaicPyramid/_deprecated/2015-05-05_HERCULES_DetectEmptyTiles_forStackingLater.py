# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
from ZumbaTools.FileManagement_Tools import *
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ####################################### FUNCTIONS, FOLDER PATHS AND BASIC VARIABLES ######################### #
searchFolder01 = "G:/HERCULES/02_Compositing/Cyprus/2000_Summer_DOY165/"
searchFolder02 = "G:/HERCULES/02_Compositing/Rest/2000_Summer_DOY165/"
tileList_filled = "G:/HERCULES/02_Compositing/00_FilledTiles.txt"
tileList_empty = "G:/HERCULES/02_Compositing/00_EmptyTiles.txt"

# ####################################### PROCESSING ########################################################## #
# (1) GET LISTS OF ALL FILES (*.HDR) IN CYPRUS AND REST LIST
print("Get files")
cyprus_hdr = GetFilesInFolderWithEnding(searchFolder01,".hdr")
rest_hdr = GetFilesInFolderWithEnding(searchFolder02,".hdr")
# LOOP THROUGH FILES
tiles_active = []
tiles_empty = []
for file in cyprus_hdr:
    f_open = open(file, "r")
    for line in f_open:
        if line.find("Band_1, Band_2, Band_3, Band_4, Band_5, Band_7") >= 0:
            tiles_active.append(file)
        if line.find(" noData, noData, noData, noData, noData, noData") >= 0:
            tiles_empty.append(file)
for file in rest_hdr:
    f_open = open(file, "r")
    for line in f_open:
        if line.find("Band_1, Band_2, Band_3, Band_4, Band_5, Band_7") >= 0:
            tiles_active.append(file)
        if line.find(" noData, noData, noData, noData, noData, noData") >= 0:
            tiles_empty.append(file)
# WRITE LIST TO OUTPUT-FILE
print("Write output")
WriteListToTXT(tiles_active, tileList_filled)
WriteListToTXT(tiles_empty, tileList_empty)
# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")