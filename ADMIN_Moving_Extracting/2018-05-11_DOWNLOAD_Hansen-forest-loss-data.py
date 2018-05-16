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
tiles = ["30N_120W", "30N_110W", "30N_100W", "30N_90W", "30N_80W", "30N_20W", "30N_10W",
		 "30N_0E", "30N_10E", "30N_20E", "30N_30E", "30N_40E", "30N_50E", "30N_60E", "30N_70E", "30N_80E",
		 "30N_90E", "30N_100E", "30N_110E", "30N_120E", "30N_130E",
		 
		 "20N_110W", "20N_100W", "20N_90W", "20N_80W", "20N_70W", "20N_20W", "20N_10W",
		 "20N_0E", "20N_10E", "20N_20E", "20N_30E", "20N_40E", "20N_50E", "20N_60E", "20N_70E", "20N_80E",
		 "20N_90E", "20N_100E", "20N_110E", "20N_120E", "20N_130E",

		 "10N_90W", "10N_80W", "10N_70W", "10N_60W", "10N_50W", "10N_20W", "10N_10W",
		 "10N_0E", "10N_10E", "10N_20E", "10N_30E", "10N_40E", "10N_50E", "10N_70E", "10N_80E",
		 "10N_90E", "10N_100E", "10N_110E", "10N_120E", "10N_130E",
		 
		 "00N_90W", "00N_80W", "00N_70W", "00N_60W", "00N_50W", "00N_40W",
		 "00N_0E", "00N_10E", "00N_20E", "00N_30E", "00N_40E",
		 "00N_90E", "00N_100E", "00N_110E", "00N_120E", "00N_130E", "00N_140E", "00N_150E", "00N_160E",
		
		 "10S_80W", "10S_70W", "10S_60W", "10S_50W", "10S_40W",
		 "10S_10E", "10S_20E", "10S_30E", "10S_40E", "10S_50E",
		 "10S_100E", "10S_110E", "10S_120E", "10S_130E", "10S_140E", "10S_150E", "10S_160E",
		
		 "20S_80W", "20S_70W", "20S_60W", "20S_50W", "20S_40W",
		 "20S_10E", "20S_20E", "20S_30E", "20S_40E", "20S_50E",
		 "20S_110E", "20S_120E", "20S_130E", "20S_140E", "20S_150E",
		 
		 "30S_80W", "30S_70W", "30S_60W", "30S_50W",
		 "30S_10E", "30S_20E", "30S_30E",
		 "30S_110E", "30S_120E", "30S_130E", "30S_140E", "30S_150E",
		 ]
# ####################################### START PROCESSING #################################################### #
for tile in tqdm(tiles):
	#print(tile)
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
		urlretrieve(f_in, f_out)
		urlretrieve(g_in, g_out)
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
