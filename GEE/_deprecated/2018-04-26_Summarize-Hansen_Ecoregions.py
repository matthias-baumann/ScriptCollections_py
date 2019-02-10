# ####################################### SET TIME-COUNT ###################################################### ##
## EXTRACT GLOBAL FOREST LOSS DATA (HANSEN ET AL) FROM GEE (Version 1.0)                                        ##
## (c) Matthias Baumann, May 2017                                                                               ##
##                                                                                                              ##
## Humboldt-University Berlin                                                                                   ##
# ####################################### IMPORT MODULES, START EARTH-ENGINE ################################## ##
import time
import osr
import ee
import csv
import ogr, json
import baumiTools as bt
from tqdm import tqdm
ee.Initialize()
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " +  starttime)
print("")
# ####################################### FILES AND FOLDER-PATHS ############################################## #
rootFolder = "D:/baumamat/"
shp = rootFolder + "WWF_potentialVeg_intersect_single.shp"
out_csv = rootFolder + "areaSummaries.csv"
# ####################################### FUNCTIONS ########################################################### #
def Build_EE_polygon(geometry):
# Transform the coordinate system into EPSG 4326 to match the EE-CS
    source_SR = geometry.GetSpatialReference()
    target_SR = osr.SpatialReference()
    target_SR.ImportFromEPSG(4326)
    trans = osr.CoordinateTransformation(source_SR, target_SR)
    geometry.Transform(trans)
# Build the EE-feature via the json-conversion
    geom_json = json.loads(geometry.ExportToJson())
    geom_coord = geom_json['coordinates']
    geom_EE = ee.Geometry.Polygon(coords=geom_coord)
    return geom_EE
# ####################################### START PREPARING THE FEATURE COLLECTION ############################## #
# Load the shapefiles, build the coordinate transformation
SHP = bt.baumiVT.CopyToMem(shp)
#SHP = ogr.Open(shp)
LYR = SHP.GetLayer()
# Build the output-list
outDS = [["ORIG_FID", "ECO_ID", "ECO_Name", "Navin_Name", "BIOME", "Prop_in_Navin",
          "F2000_km_th25", "F2000_km_th40", "FL2001_km", "FL2002_km", "FL2003_km", "FL2004_km", "FL2005_km",
          "FL2006_km", "FL2007_km", "FL2008_km", "FL2009_km", "FL2010_km", "FL2011_km", "FL2012_km","FL2013_km",
          "FL2014_km", "FL2015_km", "FL2016_km", "FL2017_km"]]
# Lop through the features
#feat = lyr.GetNextFeature()
#while feat:
for feat in tqdm(LYR):
    ecoID = int(feat.GetField("ECO_ID"))
    ecoName = feat.GetField("ECO_NAME")
    navinName = feat.GetField("Class_Name")
    biome = int(feat.GetField("BIOME"))
    prop = format(feat.GetField("AreaRatio"), '.5f')
    origFID = feat.GetField("ORIG_FID")
    ecoGEOM = feat.GetGeometryRef()
# Build an earth engine feature, then start the download
    interEE = Build_EE_polygon(ecoGEOM)
# Instantiate output
    vals = [origFID, ecoID, ecoName, navinName, biome, prop]
    processFlag = 0
    while processFlag == 0:
        try:
        # Calculate the areas of forest in 2000 based on the threshold
            gfc = ee.Image(r'UMD/hansen/global_forest_change_2017_v1_5')
            forest2000 = gfc.select(['treecover2000'])
            forMask_25 = forest2000.updateMask(forest2000.gt(25))
            forest_25 = forMask_25.reduceRegion(reducer=ee.Reducer.sum(), geometry=interEE, maxPixels=1e13, scale=30).getInfo()
            f2000_25_km2 = format(forest_25['treecover2000'] * 900 / 1000000, '.5f')
            vals.append(f2000_25_km2)
            forMask_40 = forest2000.updateMask(forest2000.gt(40))
            forest_40 = forMask_40.reduceRegion(reducer=ee.Reducer.sum(), geometry=interEE, maxPixels=1e13, scale=30).getInfo()
            f2000_40_km2 = format(forest_40['treecover2000'] * 900 / 1000000, '.5f')
            vals.append(f2000_40_km2)
        # Calculate the area of forest loss per year
            lossYear = gfc.select(['lossyear'])
            lossYR = lossYear.reduceRegion(reducer=ee.Reducer.frequencyHistogram().unweighted(), geometry=interEE, maxPixels=1e13, scale=30)
            lossYR = lossYR.get('lossyear').getInfo()
            for yr in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17']:
                px = lossYR.get(yr)
                if px == None:
                    px = 0
                else:
                    px = px
                fl_km = format(px*900/1000000, '.5f')
                vals.append(fl_km)
        # Add the val-list to the outputlist, switch processFlag to 1
            outDS.append(vals)
            processFlag = 1
        except:
            print("--> GEE timed out, waiting 3min before restarting...")
            print("   --> ", time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime()))
            time.sleep(180)
            processFlag = processFlag
# take next feature in Navin's dataset
    outDS.append(vals)
#feat = lyr.GetNextFeature()

# Write output
print("Write output")
with open(out_csv, "w") as theFile:
    csv.register_dialect("custom", delimiter = ",", skipinitialspace = True, lineterminator = '\n')
    writer = csv.writer(theFile, dialect = "custom")
    for element in outDS:
        writer.writerow(element)
# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")