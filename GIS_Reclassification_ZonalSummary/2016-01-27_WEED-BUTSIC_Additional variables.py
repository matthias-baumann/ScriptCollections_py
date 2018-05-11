# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import ogr, osr
from ZumbaTools._Vector_Tools import *
import csv

# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ############################################################################################################# #
outFile = "D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/Butsic-etal_Marihuana-California/SummaryDataset_V02_NeighbourAddon_20160420.csv"
# ####################################### OPEN FILES, BUILD COORDINATE TRANSFORMATION ######################### #
drvV = ogr.GetDriverByName('ESRI Shapefile')
drvMemV = ogr.GetDriverByName('Memory')
grows = drvMemV.CopyDataSource(ogr.Open("D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/Butsic-etal_Marihuana-California/_shpFiles_prepared/01_Grows.shp"),'')
parcel = drvMemV.CopyDataSource(ogr.Open("D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/Butsic-etal_Marihuana-California/_shpFiles_prepared/00_Parcel.shp"),'')
growsLYR = grows.GetLayer()
parcelLYR = parcel.GetLayer()
parcel_grows_tr = CoordinateTransform_Vector(parcelLYR, growsLYR)
skipList = ["05315125"]
# ####################################### GET THE FIRST FEATURE OF THE ZONE-FILE, THEN LOOP ################### #
outList = []
header = ["APN", "100m_oPlants", "100m_gPlants", "500m_oPlants", "500m_gPlants"]
outList.append(header)
zone_feat = parcelLYR.GetNextFeature()
while zone_feat:
#### Check if object in skipList
    ID = zone_feat.GetField("APN")
    if not ID in skipList:
        print("Processing APN " + str(ID))
    # Append value
        vals = []
        vals.append(ID)
    # Get the Geometry, make clone
        geom = zone_feat.GetGeometryRef()
        geom_zone = geom.Clone()
    # Count first the number of plants in the geometry itself which we later subtract from the other sums
        geom_zone.Transform(parcel_grows_tr)
        growsLYR.SetSpatialFilter(geom_zone)
        nr_points = growsLYR.GetFeatureCount()
        if nr_points == 0:
            g_plants_pol = 0
            o_plants_pol = 0
        else:
            g_plants_pol = 0
            o_plants_pol = 0
            grow_feat = growsLYR.GetNextFeature()
            while grow_feat:
                p_gh = grow_feat.GetField("g_plants")
                g_plants_pol = g_plants_pol + p_gh
                # Get number of plants in open space
                g_open = grow_feat.GetField("o_plants")
                o_plants_pol = o_plants_pol + g_open
                grow_feat = growsLYR.GetNextFeature()
            growsLYR.ResetReading()
    # Build buffer of 100m a, use buffer to set spatial filter --> map-units are in feet, so we have to convert to meters
        geom_buff = geom.Clone()
        buff100 = geom_buff.Buffer(328)
        buff100.Transform(parcel_grows_tr)
        growsLYR.SetSpatialFilter(buff100)
    # Do evaluations in the spatial filter
        nr_points = growsLYR.GetFeatureCount()
        if nr_points == 0:
            vals.append(0)
            vals.append(0)
        else:
    # Set initial plant values to 0, then loop over selected grow-points
            g_plants = 0
            o_plants = 0
            grow_feat = growsLYR.GetNextFeature()
            while grow_feat:
                p_gh = grow_feat.GetField("g_plants")
                g_plants = g_plants + p_gh
                # Get number of plants in open space
                g_open = grow_feat.GetField("o_plants")
                o_plants = o_plants + g_open
                grow_feat = growsLYR.GetNextFeature()
    # Subtract the number of points that are in the polygon itself
            o_plants = o_plants - o_plants_pol
            g_plants = g_plants - g_plants_pol
            vals.append(o_plants)
            vals.append(g_plants)
            growsLYR.ResetReading()
    # Build buffer of 500m
        buff500 = geom_buff.Buffer(1640)
        buff500.Transform(parcel_grows_tr)
        growsLYR.SetSpatialFilter(buff500)
    # Do evaluations in the spatial filter
        nr_points = growsLYR.GetFeatureCount()
        if nr_points == 0:
            vals.append(0)
            vals.append(0)
        else:
    # Set initial plant values to 0, then loop over selected grow-points
            g_plants = 0
            o_plants = 0
            grow_feat = growsLYR.GetNextFeature()
            while grow_feat:
                p_gh = grow_feat.GetField("g_plants")
                g_plants = g_plants + p_gh
                # Get number of plants in open space
                g_open = grow_feat.GetField("o_plants")
                o_plants = o_plants + g_open
                grow_feat = growsLYR.GetNextFeature()
    # Subtract the number of points that are in the polygon itself
            o_plants = o_plants - o_plants_pol
            g_plants = g_plants - g_plants_pol
            vals.append(o_plants)
            vals.append(g_plants)
            growsLYR.ResetReading()
    # Add the values to the output-list, go to next feature
        outList.append(vals)
        zone_feat = parcelLYR.GetNextFeature()
    else:
        zone_feat = parcelLYR.GetNextFeature()


# Write output-file
print("Write output")
with open(outFile, "w") as theFile:
    csv.register_dialect("custom", delimiter = ",", skipinitialspace = True, lineterminator = '\n')
    writer = csv.writer(theFile, dialect = "custom")
    for element in outList:
        writer.writerow(element)

# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")

        # shp_mem = drvV.CreateDataSource("D:/shpout2.shp")
        # lyr = shp_mem.CreateLayer('', growsLYR.GetSpatialRef(), ogr.wkbPolygon)
        # lyrDef = lyr.GetLayerDefn()
        # feat = ogr.Feature(lyrDef)
        # feat.SetGeometry(buff500)
        # lyr.CreateFeature(feat)
        # lyr.SetFeature(feat)
        #
        #
        # exit(0)