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
grid = bt.baumiVT.CopyToMem("D:/baumamat/Warfare/_SHPs/BIOMES_TropicsSavannas_10kmGrid_polygons.shp")
conflict = bt.baumiVT.CopyToMem("D:/baumamat/Warfare/_Variables/CONFLICT_DATA/PRIO/Disaggregated_Data/UCDP Georeferenced Event Dataset (GED) Global version 17.2 (2016)/ged171.shp")
outCSV = "D:/baumamat/Warfare/_DataSummaries/PRIO_data.csv"
# ####################################### PROCESSING ########################################################## #
# Initialize output, define temporal range
outDS = [["PolygonID", "Year", "Conflict_YN", "nr_events", "nr_fatalities"]]
years = range(1990, 2017)
# Get layers, do coordinate transformation
grid_lyr = grid.GetLayer()
conf_lyr = conflict.GetLayer()
transform = bt.baumiVT.CS_Transform(grid_lyr, conf_lyr)
# Loop through features
#feat = grid_lyr.GetNextFeature()
#while feat:
for feat in tqdm(grid_lyr):
# initialize values, add ID
    id = feat.GetField("UniqueID")
    #print(id)
    geom = feat.GetGeometryRef()
    geom.Transform(transform)
# Make spatial selection in conflict-lyr
    conf_lyr.SetSpatialFilter(geom)
# Now loop through the years
# Make the thematic selection of the conflict-lyr --> where_prec <= 2;
    for yr in years:
        select_statement = '(where_prec < 3) AND (year = ' + str(yr) + ')'
        conf_lyr.SetAttributeFilter(select_statement)
    # Now calculate the statistics we want to gather
        nr_events = conf_lyr.GetFeatureCount()
        nr_fatalities = 0
        conf_feat = conf_lyr.GetNextFeature()
        while conf_feat:
            deaths = conf_feat.GetField('best')
            nr_fatalities = nr_fatalities + deaths
            conf_feat = conf_lyr.GetNextFeature()
        # Reset the reading and remove attribute filter
        conf_lyr.ResetReading()
        conf_lyr.SetAttributeFilter(None)
    # Check if it is a conflict by definition of PRIO --> more than 25 deaths per year
        if nr_fatalities >= 25:
            conflict_yn = 1
        else:
            conflict_yn = 0
    # Create Value list, append to output
        vals = [id, yr, conflict_yn, nr_events, int(nr_fatalities)]
        #print(vals)
        outDS.append(vals)
# reset reading of conflict, and remove spatial filter
    conf_lyr.SetSpatialFilter(None)
    conf_lyr.ResetReading()
    #feat = grid_lyr.GetNextFeature()
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