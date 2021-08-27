# ####################################### SET TIME-COUNT ###################################################### ##
## EXTRACT LANDSAT TIME SERIES FOR POINTS (Version 1.1)                                                         ##
## (c) Matthias Baumann, March 2018                                                                             ##
## Humboldt-University Berlin                                                                                   ##
# ####################################### IMPORT MODULES, START EARTH-ENGINE ################################## ##
import time
import baumiTools as bt
import ogr
import csv
import ee
from tqdm import tqdm
import pandas as pd
ee.Initialize()
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " +  starttime)
print("")
# ####################################### FILES AND FOLDER-PATHS ############################################## #
rootFolder = "L:/_PROJECTS/_Primary_Forests_and_Droughts/"
#rootFolder = "R:/_BioGeo/_PROJECTS/_Primary_Forests_and_Droughts"
#points_PF = bt.baumiVT.CopyToMem(rootFolder + "Analysis/01_Points_PrimaryForests/01_Sample_Min2.shp")
points_control = bt.baumiVT.CopyToMem(rootFolder + "Analysis/02_Points_OtherForests/02_OtherForest_100000p_EuropeLandCover_epsg4326.shp")
#out_PF = rootFolder + "Analysis/03_PointExtraction/01_PF-sample_MatchedSample_L4578data_2021-04-09.csv"
out_control = rootFolder + "Analysis/03_PointExtraction/02_Control-sample_MatchedSample_L4578data_2021-04-09.csv"
idFile = pd.read_csv(rootFolder + "Analysis/03_PointExtraction/03_MatchedSample_UniqueIDs.csv")
# ####################################### FUNCTIONS ########################################################### #
def Retrieve_SR01_fromGEE_Point(geometry, sensor):

    # Coordinate system has to be be WGS84 (EPSG:4326)
    # Build an earth engine feature
    xCoord = geometry.GetX()
    yCoord = geometry.GetY()
    pts = {'type': 'Point', 'coordinates': [xCoord, yCoord]}

    # Get the S2-SR data
    def mask_clouds_S2(img):
        # First mask based on qa band
        qa = img.select('QA60')
        clouds = qa.bitwiseAnd(1 << 10).eq(0)
        cirrus = qa.bitwiseAnd(1 << 11).eq(0)
        full_mask = clouds.add(cirrus)
        img = img.mask(full_mask)
        # Second mask based on scene classification
        # 0: Nodata, 3: Cloud shadows, 7: unclassified, 8: cloud medium prob, 9: cloud high prob, 10: cirrus, 11: snow
        # scl = img.select('SCL').unmask(0)
        # scl_mask = scl.neq(0).\
        #     And(scl.neq(3)).\
        #     And(scl.neq(7)).\
        #     And(scl.neq(8)).\
        #     And(scl.neq(9)).\
        #     And(scl.neq(10)).\
        #     And(scl.neq(11))
        # img = img.updateMask(scl_mask)

        return img.select(['B2', 'B3', 'B4', 'B8A', 'B11', 'B12', 'SCL'],
                          ['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'SCL'])
    s2 = ee.ImageCollection('COPERNICUS/S2_SR').\
        filter(ee.Filter.date("1990-01-01", "2021-04-08")).\
        filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 75)).\
        map(mask_clouds_S2)

    # Get the collection for L
    def getQABit(image, start, end, newName):
        pattern = 0
        for i in range(start, end + 1):
            pattern += 2 ** i
        return image.select([0], [newName]).bitwiseAnd(pattern).rightShift(start)

    def mask_clouds_L4578(img):

        # Select the QA band.

        QA = img.select('pixel_qa')
        # Get the internal_cloud_algorithm_flag bit.
        shadow = getQABit(QA, 3, 3, 'cloud_shadow')
        cloud = getQABit(QA, 5, 5, 'cloud')
        water = getQABit(QA, 2, 2,'water')

        # Return an image masking out cloudy areas.
        return img.updateMask(cloud.eq(0)).updateMask(shadow.eq(0).updateMask(water.eq(0)))


    # Landsat 8
    L8 = ee.ImageCollection('LANDSAT/LC08/C01/T1_SR').\
        filter(ee.Filter.date("1990-01-01", "2021-04-08")).\
        select(['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'pixel_qa'], ['B', 'G', 'R', 'NIR', 'SWIR1', 'SWIR2', 'pixel_qa']).\
        map(mask_clouds_L4578)
    # Landsat 7
    L7 = ee.ImageCollection('LANDSAT/LE07/C01/T1_SR').\
        filter(ee.Filter.date("1990-01-01", "2021-04-08")).\
        select(['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'pixel_qa'], ['B', 'G', 'R', 'NIR', 'SWIR1', 'SWIR2', 'pixel_qa']).\
        map(mask_clouds_L4578)
    # Landsat 5
    L5 = ee.ImageCollection('LANDSAT/LT05/C01/T1_SR').\
        filter(ee.Filter.date("1990-01-01", "2021-04-08")).\
        select(['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'pixel_qa'], ['B', 'G', 'R', 'NIR', 'SWIR1', 'SWIR2', 'pixel_qa']).\
        map(mask_clouds_L4578)
    # Landsat 4
    L4 = ee.ImageCollection('LANDSAT/LT04/C01/T1_SR').\
        filter(ee.Filter.date("1990-01-01", "2021-04-08")).\
        select(['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'pixel_qa'], ['B', 'G', 'R', 'NIR', 'SWIR1', 'SWIR2', 'pixel_qa']).\
        map(mask_clouds_L4578)
    # All Landsat
    L_all = ee.ImageCollection(L4.merge(L5).merge(L7).merge(L8)).select(['B', 'G', 'R', 'NIR', 'SWIR1', 'SWIR2'], ['blue', 'green', 'red', 'nir', 'swir1', 'swir2'])

    if sensor=="Landsat":
        values_all = L_all.getRegion(pts, 30).getInfo()
    if sensor=="S2":
        values_all = s2.getRegion(pts, 10).getInfo()

    return values_all

# ####################################### COLLECT THE VALUES PER POINT ######################################## #
print("Get IDs that we want to extract")
ids = idFile['Other'].to_list()

print("Extract values for points in SHP-file")
valueList = [["UniqueID", "Scene_ID", "Date", "MGRS_TILE", 'blue', 'green', 'red', 'nir', 'swir1', 'swir2']]
lyr = points_control.GetLayer()
coord = lyr.GetSpatialRef()
nFeat = lyr.GetFeatureCount()
feat = lyr.GetNextFeature()
while feat:
    Pid = feat.GetField("ID")
    if Pid in ids:
        print(Pid)
    # Now get the geometry and do stuff
        geom = feat.GetGeometryRef()
# Now extract the individual data from the collections based on the definitions above
#         # Sentinel-2
#         vals_S2 = Retrieve_SR01_fromGEE_Point(geometry=geom, sensor="S2")
#         for i in range(1, len(vals_S2)):
#             obs = vals_S2[i]
#             # Make the check for the SCL data value
#             scl_check = [0, 3, 7, 8, 9, 10, 11]
#             if obs[10] not in scl_check:
#                 if not any(v is None for v in obs):
#                     val = [Pid, obs[0], obs[0][0:8], obs[0][-6:], obs[4], obs[5], obs[6], obs[7], obs[8], obs[9]]
#                     valueList.append(val)
        # Landsat
        vals_L = Retrieve_SR01_fromGEE_Point(geometry=geom, sensor="Landsat")
        for i in range(1,len(vals_L)):
            obs = vals_L[i]
            LID = obs[0]
            idStart = LID.find("L")
            imgID = LID[idStart:]
            dateStart = LID.rfind("_")
            imgDate = LID[dateStart+1:]
            if not any(v is None for v in obs):
                val = [Pid, imgID, imgDate, "NA", obs[4], obs[5], obs[6], obs[7], obs[8], obs[9]]
                valueList.append(val)
# Get next feature
    feat = lyr.GetNextFeature()
# ##################################### WRITE OUTPUT ######################################################## #
print("Write output")
bt.baumiFM.WriteListToCSV(out_control, valueList, ",")
# ##################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")