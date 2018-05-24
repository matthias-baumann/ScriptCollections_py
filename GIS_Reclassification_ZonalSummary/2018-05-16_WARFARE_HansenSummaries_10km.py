# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
from tqdm import tqdm
import time
import baumiTools as bt
import gdal
import numpy as np
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" + starttime)
print("")
# ####################################### FOLDER PATHS AND BASIC VARIABLES #################################### #
shape = bt.baumiVT.CopyToMem("D:/baumamat/Warfare/_SHPs/BIOMES_TropicsSavannas_10kmGrid_polygons.shp")
f = gdal.Open("D:/baumamat/Warfare/_Variables/Forest/Forest2000.vrt")
fl = gdal.Open("D:/baumamat/Warfare/_Variables/Forest/LossYear.vrt")
g = gdal.Open("D:/baumamat/Warfare/_Variables/Forest/Gain.vrt")
outCSV = "D:/baumamat/Warfare/_DataSummaries/ForestLossData.csv"
# ####################################### PROCESSING ########################################################## #
# Initialize output
outDS = [["PolygonID", "TC2000_mean", "%For2000_ge25", "FL01_km", "FL02_km", "FL03_km", "FL04_km", "FL05_km", "FL06_km",
          "FL07_km", "FL08_km", "FL09_km", "FL10_km", "FL11_km", "FL12_km", "FL13_km", "FL14_km", "FL15_km", "FL16_km",
          "gain_km"]]
# Get layer, start looping through features
lyr = shape.GetLayer()
#feat = lyr.GetNextFeature()
#while feat:
for feat in tqdm(lyr):
    # initialize values, add ID
    vals = []
    id = feat.GetField("UniqueID")
    #print(id)
    vals.append(id)
    geom = feat.GetGeometryRef()
# Get the mean % tree-cover value and percentage coverage
    try:
        geom_np, forest_np = bt.baumiRT.Geom_Raster_to_np(geom, f)
        meanTC = np.mean(forest_np)
        perF = np.size(forest_np[forest_np>30]) / np.size(forest_np) * 100
        vals.extend(["{:4.2f}".format(meanTC), "{:4.2f}".format(perF)])
# Get the loss per year --> calculate #px *28x28 to get km2
        geom_np, loss_np = bt.baumiRT.Geom_Raster_to_np(geom, fl)
        for yr in range(1, 17):
            nr_px = np.size(loss_np[loss_np==yr])
            loss_km = (nr_px * 28 * 28) / 1000000
            vals.append("{:6.4f}".format(loss_km))
# Get the gain --> calculate #px *28x28 to get km2
        geom_np, gain_np = bt.baumiRT.Geom_Raster_to_np(geom, g)
        gain_px = np.size(gain_np[gain_np==1])
        gain_km2 = (gain_px * 28 * 28) / 1000000
        vals.append("{:6.4f}".format(gain_km2))
    except:
        print(id, "could not be processed, check manually.")
        vals.extend(['NA'] * 20)
# Attach values to the outlist, get next feature
    outDS.append(vals)
    #feat = lyr.GetNextFeature()
# Write output
print("Write output")
bt.baumiFM.WriteListToCSV(outCSV, outDS, ",")

# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")