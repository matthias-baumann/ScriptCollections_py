# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import os
import time
from urllib.request import urlretrieve
from tqdm import tqdm
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" + starttime)
print("")
# ####################################### FOLDER PATHS AND FUNCTIONS ########################################## #
dl_Folder = "D:/baumamat/Warfare/_Variables/Forest/"
baseURL = "https://storage.googleapis.com/earthenginepartners-hansen/GFC-2016-v1.4/Hansen_GFC-2016-v1.4"
layers = [["_treecover2000_", "Forest2000"], ["_gain_", "Gain"], ["_lossyear_", "LossYear"]]
ext = ".tif"
tiles = ["40N_130W", "40N_120W", "40N_110W", "40N_100W", "40N_090W", "40N_080W", "40N_010W",
		 "40N_000E", "40N_010E", "40N_020E", "40N_030E", "40N_040E", "40N_050E", "40N_060E", "40N_070E", "40N_080E",
		 "40N_090E", "40N_100E", "40N_110E", "40N_120E", "40N_130E", "40N_140E",

         "30N_120W", "30N_110W", "30N_100W", "30N_090W", "30N_080W", "30N_020W", "30N_010W",
		 "30N_000E", "30N_010E", "30N_020E", "30N_030E", "30N_040E", "30N_050E", "30N_060E", "30N_070E", "30N_080E",
		 "30N_090E", "30N_100E", "30N_110E", "30N_120E", "30N_130E",
		 
		 "20N_110W", "20N_100W", "20N_090W", "20N_080W", "20N_070W", "20N_020W", "20N_010W",
		 "20N_000E", "20N_010E", "20N_020E", "20N_030E", "20N_040E", "20N_050E", "20N_060E", "20N_070E", "20N_080E",
		 "20N_090E", "20N_100E", "20N_110E", "20N_120E", "20N_130E",

		 "10N_090W", "10N_080W", "10N_070W", "10N_060W", "10N_050W", "10N_020W", "10N_010W",
		 "10N_000E", "10N_010E", "10N_020E", "10N_030E", "10N_040E", "10N_050E", "10N_070E", "10N_080E",
		 "10N_090E", "10N_100E", "10N_110E", "10N_120E", "10N_130E",
		 
		 "00N_090W", "00N_080W", "00N_070W", "00N_060W", "00N_050W", "00N_040W",
		 "00N_000E", "00N_010E", "00N_020E", "00N_030E", "00N_040E",
		 "00N_090E", "00N_100E", "00N_110E", "00N_120E", "00N_130E", "00N_140E", "00N_150E", "00N_160E",
		
		 "10S_080W", "10S_070W", "10S_060W", "10S_050W", "10S_040W",
		 "10S_010E", "10S_020E", "10S_030E", "10S_040E", "10S_050E",
		 "10S_100E", "10S_110E", "10S_120E", "10S_130E", "10S_140E", "10S_150E", "10S_160E",
		
		 "20S_080W", "20S_070W", "20S_060W", "20S_050W", "20S_040W",
		 "20S_010E", "20S_020E", "20S_030E", "20S_040E", "20S_050E",
		 "20S_110E", "20S_120E", "20S_130E", "20S_140E", "20S_150E",
		 
		 "30S_080W", "30S_070W", "30S_060W", "30S_050W",
		 "30S_010E", "30S_020E", "30S_030E",
		 "30S_110E", "30S_120E", "30S_130E", "30S_140E", "30S_150E",
		 ]
# ####################################### START PROCESSING #################################################### #
for tile in tiles:
	print(tile)
	# Forest
	f_in = baseURL + layers[0][0] + tile + ext
	f_out = dl_Folder + layers[0][1] + "/" + tile + ext
	# Gain
	g_in = baseURL + layers[1][0] + tile + ext
	g_out = dl_Folder + layers[1][1] + "/" + tile + ext
	# Loss
	l_in = baseURL + layers[2][0] + tile + ext
	l_out = dl_Folder + layers[2][1] + "/" + tile + ext
	try:
		if not os.path.exists(f_out):
			urlretrieve(f_in, f_out)
		if not os.path.exists(g_out):
			urlretrieve(g_in, g_out)
		if not os.path.exists(l_out):
			urlretrieve(l_in, l_out)
	except:
		print("Tile ", tile, " does not exist. Skipping...")
# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")
