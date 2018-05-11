# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import shutil
import os
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ####################################### FUNCTIONS, FOLDER PATHS AND BASIC VARIABLES ######################### #
tileList_empty = "G:/HERCULES/02_Compositing/00_EmptyTiles.txt"

# ####################################### PROCESSING ########################################################## #
# (1) OPEN EMPTY-TILE-LIST-FILE, THEN COPY THE FILES
f_open = open(tileList_empty, "r")
for outpath in f_open:
    outpath = outpath[:-1]
    print(outpath)
    # For the hdr file
    inpath = outpath
    inpath = inpath.replace("/2000_Summer_DOY165/","/2000_Spring_DOY95/")
    if not os.path.exists(outpath):
        shutil.copy(inpath, outpath)
    else:
        print("Destination already exists. Skipping...")
    # For the bsq file
    inpath = inpath.replace(".hdr", ".bsq")
    outpath = outpath.replace(".hdr", ".bsq")
    if not os.path.exists(outpath):
        shutil.copy(inpath, outpath)
    else:
        print("Destination already exists. Skipping...")


# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")


# PARTS BELOW ARE FROM COPYING. DID NOT WORK FOR SOME REASON, SO THE CODE ABOVE WAS MADE TO COPY THE EMPTY TILES FROM THE SPRING COMPOSITE BACK

# # (3-1) CYPRUS
# deletelist_cyprus = []
# for tile in cyprus_tiles:
#     p1 = tile.rfind("/")
#     p2 = tile.rfind("_1998-2002_")
#     tile = tile[p1+1:p2+1]
#     for item in os.listdir(cyprus):
#         if item.find(tile) >= 0:
#             path = cyprus + item
#             deletelist_cyprus.append(path)
# for item in deletelist_cyprus:
#     try:
#         print(item)
#         os.remove(item)
#     except:
#         print("Already removed. Skipping...")
# print("")
# # (3-1) REST
# deletelist_rest = []
# for tile in rest_tiles:
#     p1 = tile.rfind("/")
#     p2 = tile.rfind("_1998-2002_")
#     tile = tile[p1+1:p2+1]
#     for item in os.listdir(rest):
#         if item.find(tile) >= 0:
#             path = rest + item
#             deletelist_rest.append(path)
# for item in deletelist_rest:
#     try:
#         print(item)
#         os.remove(item)
#     except:
#         print("Already removed. Skipping...")