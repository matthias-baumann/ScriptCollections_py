# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import os
import time
from urllib.request import urlretrieve
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" + starttime)
print("")
# ####################################### FOLDER PATHS AND FUNCTIONS ########################################## #
dl_Folder = "L:/_PROJECTS/_CORONA-RECTIFICATION_/_PROJECTS/_CHACO/_00_RAW_DOWNLOADS/NEW_Order/"
baseURL = "https://dds.cr.usgs.gov/orders/0102007105593/"
files = ['DS1022-1029DA022_a.tif', "DS1022-1029DA022_b.tif", "DS1022-1029DA022_c.tif", "DS1022-1029DA022_d.tif",
         "DS1022-1029DA023_a.tif", "DS1022-1029DA023_b.tif", "DS1022-1029DA023_c.tif", "DS1022-1029DA023_d.tif",
         "DS1022-1029DA024_a.tif", "DS1022-1029DA024_b.tif", "DS1022-1029DA024_c.tif", "DS1022-1029DA024_d.tif",
         "DS1022-1029DA028_a.tif", "DS1022-1029DA028_b.tif", "DS1022-1029DA028_c.tif", "DS1022-1029DA028_d.tif",
         "DS1022-1029DA029_a.tif", "DS1022-1029DA029_b.tif", "DS1022-1029DA029_c.tif", "DS1022-1029DA029_d.tif",
         "DS1022-1029DA030_a.tif", "DS1022-1029DA030_b.tif", "DS1022-1029DA030_c.tif", "DS1022-1029DA030_d.tif",
         "DS1022-1029DA031_a.tif", "DS1022-1029DA031_b.tif", "DS1022-1029DA031_c.tif", "DS1022-1029DA031_d.tif",
         "DS1022-1029DF016_a.tif", "DS1022-1029DF016_b.tif", "DS1022-1029DF016_c.tif", "DS1022-1029DF016_d.tif",
         "DS1022-1029DF017_a.tif", "DS1022-1029DF017_b.tif", "DS1022-1029DF017_c.tif", "DS1022-1029DF017_d.tif",
         "DS1022-1029DF018_a.tif", "DS1022-1029DF018_b.tif", "DS1022-1029DF018_c.tif", "DS1022-1029DF018_d.tif",
         "DS1022-1029DF022_a.tif", "DS1022-1029DF022_b.tif", "DS1022-1029DF022_c.tif", "DS1022-1029DF022_d.tif",
         "DS1022-1029DF023_a.tif", "DS1022-1029DF023_b.tif", "DS1022-1029DF023_c.tif", "DS1022-1029DF023_d.tif",
         "DS1022-1029DF024_a.tif", "DS1022-1029DF024_b.tif", "DS1022-1029DF024_c.tif", "DS1022-1029DF024_d.tif",
         "DS1022-1029DF025_a.tif", "DS1022-1029DF025_b.tif", "DS1022-1029DF025_c.tif", "DS1022-1029DF025_d.tif"]
# ####################################### START PROCESSING #################################################### #
for file in files:
    in_file = baseURL + file
    out_file = dl_Folder + file
    print(out_file)
    # DOWNLOAD
    if not os.path.exists(out_file):
        urlretrieve(in_file, out_file)
# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")
