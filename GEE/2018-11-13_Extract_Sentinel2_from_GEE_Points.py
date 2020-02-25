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
root_folder = 'D:/_TEACHING/__Classes-Modules_HUB/MSc-M1_Quantitative-Methods/WS_2019-2020/Data/'
shp = ogr.Open(root_folder + "Locations_newALL.shp")
output = root_folder + "Sentinel-2_SR/Sentinel-2_SR-data_20200112.csv"
# ####################################### SEARCH PARAMETERS ################################################### #
startDate = '2000-01-01'
endDate = '2019-12-31'
# ####################################### FUNCTIONS ########################################################### #
def Retrieve_SR01_fromGEE_Point(geometry, startDate, endDate):
    # startDate & endDate has to be in the format "2018-01-01"
    # Coordinate system has to be be WGS84 (EPSG:4326)
    # Material for masking
    def mask_clouds(img):
        qa = img.select('QA60')
        clouds = qa.bitwiseAnd(1 << 10).eq(0)
        cirrus = qa.bitwiseAnd(1 << 11).eq(0)
        full_mask = clouds.add(cirrus)
        return img.updateMask(full_mask).divide(10000)

    # Make band selection
    s2bands = ee.List(['B4', 'B8', 'QA60'])
    s2band_names = ee.List(['R', 'NIR', 'QA60'])

    # Build an earth engine feature
    xCoord = geometry.GetX()
    yCoord = geometry.GetY()
    pts = {'type': 'Point', 'coordinates': [xCoord, yCoord]}
    # Now extract the individual data from the collections based on the definitions above
    s2 = ee.ImageCollection('COPERNICUS/S2_SR').\
        filter(ee.Filter.date(startDate, endDate)).\
        select(s2bands, s2band_names).\
        map(mask_clouds)

    # Merge
    values_all = s2.getRegion(pts, 30).getInfo()
    return values_all



# ####################################### COLLECT THE VALUES PER POINT ######################################## #
print("Extract values for points in SHP-file")
valueList = []
lyr = shp.GetLayer()
coord = lyr.GetSpatialRef()
nFeat = lyr.GetFeatureCount()
feat = lyr.GetNextFeature()
while feat:
#for feat in tqdm(lyr):
# Extract ID-Info from SHP-file and other informations
    Pid = feat.GetField("Id")
    print("Processing Point ID " + str(Pid))
# Now get the geometry and do stuff
    geom = feat.GetGeometryRef()
# Now extract the individual data from the collections based on the definitions above
    vals = Retrieve_SR01_fromGEE_Point(geometry=geom, startDate=startDate, endDate=endDate)
# Add to the header-line the Variable-Name Point-ID, and add it to each element as well
    vals[0].append("Point-ID")
    for i in range(1,len(vals)):
        vals[i].append(Pid)
# Remove right away the masked values, and some remnants from the sceneID
#    val_reduced = []
 #   for val in vals:
  #      if not None in val:
   #         val_reduced.append(val)
# Append to output then get next feature
    valueList.append(vals)
    feat = lyr.GetNextFeature()
# ##################################### WRITE OUTPUT ######################################################## #
print("Write output")
with open(output, "w") as theFile:
    csv.register_dialect("custom", delimiter=",", skipinitialspace=True, lineterminator='\n')
    writer = csv.writer(theFile, dialect="custom")
    # Write the complete set of values (incl. the header) of the first entry
    for element in valueList[0]:
        writer.writerow(element)
    valueList.pop(0)
    # Now write the remaining entries, always pop the header
    for element in valueList:
        element.pop(0)
        for row in element:
            writer.writerow(row)
# ##################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")