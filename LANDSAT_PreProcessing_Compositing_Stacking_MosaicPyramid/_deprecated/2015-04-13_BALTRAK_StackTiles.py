# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import os
import time
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ####################################### FUNCTIONS, FOLDER PATHS AND BASIC VARIABLES ######################### #
root_folder = "X:/Baltrak/02_Compositing_NEW/"
folders_to_stack = ["1990_Spring_DOY121", "1990_Summer_DOY180", "1990_Fall_DOY260", "1990_Metrics",
                    "2000_Spring_DOY121", "2000_Summer_DOY180", "2000_Fall_DOY260", "2000_Metrics",
                    #"2010_Spring_DOY121", "2010_Summer_DOY180", "2010_Fall_DOY260", "2010_Metrics",
                    "2014_Spring_DOY121", "2014_Summer_DOY180", "2014_Fall_DOY260", "2014_Metrics"]
out_folder = "G:/BALTRAK/00_StackedTiles02/"
# ####################################### PROCESSING ########################################################## #
# (1) GET LISTS OF TILES FOR THE YEARS WE WANT TO STACK
list_list = []
# Take the first folder to create the index
base_folder = root_folder + folders_to_stack[0] + "/"
base_list = [input for input in os.listdir(base_folder) if input.endswith('.bsq')]
print("Build List with files")
#for base in base_list:
base = base_list[0]
# Establish sublist for tupel
combo = []
# Derive tile-stems
p = base.find("_19")
tile_ID = base[:p+1]
# Loop through combinations
for folder in folders_to_stack:
    print(folder)
    searchfolder = root_folder + folder + "/"
    base_list = [input for input in os.listdir(searchfolder) if input.endswith('.bsq') and input.find(tile_ID) >= 0]
    path = searchfolder + base_list[0]
    combo.append(path)
list_list.append(combo)

# (2) STACK THE FILES IN TUPELS TOGETHER
# Stack the tiles together
for combo in list_list:
    print("Processing tile: " + str((list_list.index(combo))+1) + " of " + str(len(list_list)))
    # Build the outputname
    ID = combo[0]
    p1 = ID.rfind("/")
    p2 = ID.find("_PBC")
    tile_ID = ID[p1+1:p2+1]
    outTileName = out_folder + tile_ID + "1990-2000-2015_Imagery-Metrics_Stack.bsq"
# Build outTilePath and command
    command = "gdal_merge.py -of ENVI -separate -o " + outTileName + " "
    for c in combo:
        command = command + c + " "
# Execute the command
    if not os.path.exists(outTileName):
        os.system(command)
    else:
        print("--> Already processed. Skipping...")
# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")