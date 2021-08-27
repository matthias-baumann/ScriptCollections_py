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
dl_Folder = "D:/baumamat/Hansen_GFC-2020-v1.8/"
baseURL = "https://storage.googleapis.com/earthenginepartners-hansen/GFC-2020-v1.8/Hansen_GFC-2020-v1.8"
layers = [["_treecover2000_", "Forest2000"], ["_gain_", "Gain"], ["_lossyear_", "LossYear"]]
ext = ".tif"
x_dir = ['180W', '170W', '160W', '150W', '140W', '130W', '120W', '110W', '100W', '090W', '080W', '070W', '060W', '050W', '040W', '030W', '020W', '010W',
         '000E', '010E', '020E', '030E', '040E', '050E', '060E', '070E', '080E', '090E', '100E', '110E', '120E', '130E', '140E', '150E', '160E', '170E']
y_dir = ['80N', '70N', '60N', '50N', '40N', '30N', '20N', '10N', '00N', '10S', '20S', '30S', '40S', '50S']
# ####################################### START PROCESSING #################################################### #
for y in y_dir:
    for x in x_dir:
        # Forest
        f_in = baseURL + layers[0][0] + y + "_" + x + ext
        f_out = dl_Folder + layers[0][1] + "/" + y + "_" + x + ext
        # Gain
        g_in = baseURL + layers[1][0] + y + "_" + x + ext
        g_out = dl_Folder + layers[1][1] + "/" + y + "_" + x + ext
        # Loss
        l_in = baseURL + layers[2][0] + y + "_" + x + ext
        l_out = dl_Folder + layers[2][1] + "/" + y + "_" + x + ext
        # DOWNLOAD
        if not os.path.exists(f_out):
            print(f_out)
            urlretrieve(f_in, f_out)
        if not os.path.exists(g_out):
            urlretrieve(g_in, g_out)
        if not os.path.exists(l_out):
            print(l_out)
            urlretrieve(l_in, l_out)
# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")
