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
ee.Initialize()
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " +  starttime)
print("")
# ####################################### FILES AND FOLDER-PATHS ############################################## #
root_folder = 'D:/OneDrive - Conservation Biogeography Lab/_RESEARCH/Projects_Active/DirkSachse_Chaco/NaturalGrasslands_DataExtraction/'
shp = ogr.Open(root_folder + "Bermejo_TOC_SHP.shp")
output = root_folder + "Bermejo_TOC_SHP_S2-data.csv"
# ####################################### FUNCTIONS ########################################################### #
def Retrieve_SR01_fromGEE_Point(geometry, year):

    # Coordinate system has to be be WGS84 (EPSG:4326)
    # Material for masking
    def mask_clouds(img):
        qa = img.select('QA60')
        clouds = qa.bitwiseAnd(1 << 10).eq(0)
        cirrus = qa.bitwiseAnd(1 << 11).eq(0)
        full_mask = clouds.add(cirrus)
        return img.updateMask(full_mask).divide(10000)
    def Calc_Index(img):
        # EVI
        #evi = img.expression('2.5 * ((NIR - R) / (NIR + 6 * R - 7.5 * B + 1))', {'NIR': img.select('NIR'), 'R': img.select('R'), 'B': img.select('B')}).rename('EVI')
        #evi = evi.multiply(10000).int()
        # NDMI
        ndmi = img.normalizedDifference(['NIR', 'SWIR1']).rename('NDMI')
        ndmi = ndmi.multiply(10000).int()
        return ndmi

    # Determine Start- and End from Variable 'Year'
    start = ee.Date.fromYMD(year, 1, 1)
    end = ee.Date.fromYMD(year, 12, 31)


    # Make band selection
    s2bands = ee.List(['B2','B4', 'B8', 'B11', 'QA60'])
    s2band_names = ee.List(['B', 'R', 'NIR', 'SWIR1', 'QA60'])

    # Build an earth engine feature
    xCoord = geometry.GetX()
    yCoord = geometry.GetY()
    pts = {'type': 'Point', 'coordinates': [xCoord, yCoord]}
    # Now extract the individual data from the collections based on the definitions above
    # Before 2017 --> Sentinel 2 TOA
    if year < 2017:
        s2_index = ee.ImageCollection('COPERNICUS/S2'). \
            filter(ee.Filter.date(start, end)). \
            select(s2bands, s2band_names). \
            filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)). \
            map(mask_clouds). \
            map(Calc_Index)
    else:
        # Since 2017 --> Sentinel 2 SR
        s2_index = ee.ImageCollection('COPERNICUS/S2_SR').\
            filter(ee.Filter.date(start, end)).\
            select(s2bands, s2band_names).\
            filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)).\
            map(mask_clouds).\
            map(Calc_Index)
    # Merge
    values_all = s2_index.getRegion(pts, 10).getInfo()
    return values_all

# ####################################### COLLECT THE VALUES PER POINT ######################################## #
print("Extract values for points in SHP-file")
valueList = [["Point_Identifier", "Year", "Scene_ID", "Date", "TOA_SR", "Index", "Value"]]
identifierList = []
lyr = shp.GetLayer()
coord = lyr.GetSpatialRef()
nFeat = lyr.GetFeatureCount()
feat = lyr.GetNextFeature()
while feat:
#for feat in tqdm(lyr):
# Extract ID-Info from SHP-file and other informations
    Pid = feat.GetField("Identifier")
    yr = feat.GetField("Year")
    if not Pid in identifierList:
        # If not in the list yet, add the id to the list, then extract the data
        identifierList.append(Pid)
        print("Processing Point Identifier " + str(Pid))
    # Now get the geometry and do stuff
        geom = feat.GetGeometryRef()
# Now extract the individual data from the collections based on the definitions above
        try:
            vals = Retrieve_SR01_fromGEE_Point(geometry=geom, year=yr)
            index = vals[0][4]
            if yr < 2017:
                toa_sr = "TOA"
            else:
                toa_sr = "SR"
            for i in range(1, len(vals)+1):
                obs = vals[i]
                val = [Pid, yr, obs[0], obs[0][0:8], toa_sr, index, obs[4]]
                valueList.append(val)
        except:
            val = [Pid, yr, -9999, -9999, -9999, -9999, -9999]
            valueList.append(val)
# Get next feature
    feat = lyr.GetNextFeature()
# ##################################### WRITE OUTPUT ######################################################## #
print("Write output")
bt.baumiFM.WriteListToCSV(output, valueList, ",")
# ##################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")