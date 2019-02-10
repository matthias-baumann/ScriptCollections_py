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
import baumiTools as bt
from tqdm import tqdm
ee.Initialize()
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " +  starttime)
print("")
# ####################################### FILES AND FOLDER-PATHS ############################################## #
shp = 'D:/Warfare/_SHPs/BIOMES_TropicsSavannas_10kmGrid_polygons_testsub.shp'
outcsv = 'D:/Warfare/_DataSummaries/ForestLossData_02.csv'
# ####################################### FUNCTIONS ########################################################### #

# ####################################### START PREPARING THE FEATURE COLLECTION ############################## #
# Load the shapefile, build the coordinate transformation
shape = bt.baumiVT.CopyToMem(shp)
lyr = shape.GetLayer()
source_SR = lyr.GetSpatialRef()
target_SR = osr.SpatialReference()
target_SR.ImportFromEPSG(4326)
transform = osr.CoordinateTransformation(source_SR, target_SR)
# Build the output-list
outList = []
header = ["PolID", "%For2000", "FL2001_km", "FL2002_km", "FL2003_km", "FL2004_km", "FL2005_km", "FL2006_km",
          "FL2007_km", "FL2008_km", "FL2009_km", "FL2010_km", "FL2011_km", "FL2012_km", "FL2013_km", "FL2014_km", "FL2015_km", "FL2016_km"]
outList.append(header)
# Lop through the features
#feat = lyr.GetNextFeature()
#while feat:
for feat in tqdm(lyr):
    polID = feat.GetField("UniqueID")
    #print(polID)
    vals = [polID]
# Build an earth engine feature
    geom = feat.GetGeometryRef()
    geom.Transform(transform)
    env = geom.GetEnvelope()  # Get Envelope returns a tuple (minX, maxX, minY, maxY)
    UL = [env[0], env[3]]  # UR = [env[1], env[3]]
    LR = [env[1], env[2]]  # LL = [env[0], env[2]]
    poly = ee.Geometry.Rectangle(coords=[UL, LR])
# Select the bands from the Forest dataset
    gfc2016 = ee.Image(r'UMD/hansen/global_forest_change_2016_v1_4')
    forest2000 = gfc2016.select(['treecover2000'])
    lossYear = gfc2016.select(['lossyear'])
# Calculate the annual sums
    def calcAnnualSum(imageCollection):
        myList = ee.List([])










    #gain = gfc2016.select(['gain'])
# Extract the values into np-arrays
    # Mean Tree-Cover in square in 2000
    forest_mean = forest2000.reduceRegion(reducer=ee.Reducer.mean(), geometry=poly, maxPixels=1e13)#, scale=1000)
    forest_mean = forest_mean.get('treecover2000').getInfo()
    vals.append(forest_mean)
    print(forest_mean)
    # % of area with > 30% Tree Cover
    mask = forest2000.updateMask(forest2000.gt(30))
    #forest_hist = mask.reduceRegion(reducer=ee.Reducer.frequencyHistogram(), geometry=poly, maxPixels=1e13)#, scale=1000)
    #f_hist = forest_hist.get('treecover2000').getInfo()
    for2000_ge30 = forest2000.multiply(ee.Image.pixelArea()).divide(100000).select([0], ["areacover"])

    print(for2000_ge30)
    exit(0)
    nf = f_hist.get('null')
    if nf == None:
        nf = 0
    else:
        nf = nf
    nf_km = nf*900/1000000
    liste = list(f_hist.keys())
    f = 0
    for l in liste:
        if l != 'null':
            value = f_hist.get(str(l))
            f = f + value
    f_km = f*900/1000000
    f_prop = f_km / (f_km + nf_km)
    vals.append(f_prop)
    # Loss per year --> select manually the
    lossYR = lossYear.reduceRegion(reducer=ee.Reducer.frequencyHistogram().unweighted(), geometry=poly, maxPixels=1e13, scale=30)
    lossYR = lossYR.get('lossyear').getInfo()
    for yr in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16']:
        px = lossYR.get(yr)
        if px == None:
            px = 0
        else:
            px = px
        fl_km = px*900/1000000
        vals.append(fl_km)
# Add the val-list to the outputlist, take next featyure
    outList.append(vals)
    #feat = lyr.GetNextFeature()
# Write output
print("Write output")
with open(outcsv, "w") as theFile:
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