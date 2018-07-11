import time

starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("Starting process, time: " + starttime)
print("--------------------------------------------------------")
print("")

##############################################################################
from osgeo import ogr, osr, gdal
import struct
#import geopandas as gpd
#import pandas as pd
###############################################################################

root_folder = "F:/Lehre/SS_2018/M7_Geoprocessing in python/Week09 - Real world problems II - point intersect/Assignment07/"

driver = ogr.GetDriverByName("ESRI Shapefile")

# Points shapefile
PO = driver.Open(root_folder + 'Points.shp',0)
PO_lyr = PO.GetLayer()
srs = PO_lyr.GetSpatialRef()

# Old Growth Polygons shapefile
OG = driver.Open(root_folder + 'Old_Growth.shp',0)
OG_lyr = OG.GetLayer()
tsr_OG = OG_lyr.GetSpatialRef()
trans_OG = osr.CoordinateTransformation(srs, tsr_OG)

# private lands polygon shapefile
PL = driver.Open(root_folder + 'PrivateLands.shp',0)
PL_lyr = PL.GetLayer()
tsr_PL = PL_lyr.GetSpatialRef()
trans_PL = osr.CoordinateTransformation(srs, tsr_PL)

# Elevation Tif
EL = gdal.Open(root_folder + "Elevation.tif")
EL_pro = EL.GetProjection()
EL_tsr = osr.SpatialReference()
EL_tsr.ImportFromWkt(EL_pro)
trans_EL = osr.CoordinateTransformation(srs, EL_tsr)

# Distance to road Tif
DR = gdal.Open(root_folder + "DistToRoad.tif")
DR_pro = DR.GetProjection()
DR_tsr = osr.SpatialReference()
DR_tsr.ImportFromWkt(DR_pro)
trans_DR = osr.CoordinateTransformation(srs, DR_tsr)



PO_feat = PO_lyr.GetNextFeature()
df = list()

while PO_feat:
    id = PO_feat.GetField('Id')
    print("ID: ", id)
    geom = PO_feat.GetGeometryRef()

    # elevation
    geom_copy = geom.Clone()
    geom_copy.Transform(trans_EL)
    EL_gt = EL.GetGeoTransform()
    x, y = geom_copy.GetX(), geom_copy.GetY()
    EL_px = int((x - EL_gt[0]) / EL_gt[1])
    EL_py = int((y - EL_gt[3]) / EL_gt[5])
    EL_band = EL.GetRasterBand(1)
    EL_struc_var = EL_band.ReadRaster(EL_px, EL_py,1 ,1)
    elev = struct.unpack('H', EL_struc_var)
    elevation = elev[0]
    print("Elevation of ID ", id, "is", elevation)
    # road
    geom_copy = geom.Clone()
    geom_copy.Transform(trans_DR)
    DR_gt = DR.GetGeoTransform()
    x, y = geom_copy.GetX(), geom_copy.GetY()
    DR_px = int((x - DR_gt[0]) / DR_gt[1])
    DR_py = int((y - DR_gt[3]) / DR_gt[5])
    DR_band = DR.GetRasterBand(1)
    DR_struc_var = DR_band.ReadRaster(DR_px, DR_py, 1, 1)
    dist = struct.unpack('f', DR_struc_var)
    distance = dist[0]
    print("Distance of Point with ID", id, "to a road is about", distance,"meters")
    # point in old_growth area
    geom_copy = geom.Clone()
    geom_copy.Transform(trans_OG)
    OG_lyr.SetSpatialFilter(geom_copy)
    # featCount = OG_lyr.GetFeatureCount()
    # if featCount > 0:
    #     OG = 1
    #     print('Point is in OG area')
    #     print("")
    # else:
    #     OG = 0
    #     print('Point is NOT in OG area')
    #     print("")
    # OG_lyr.SetSpatialFilter(None)
    # point in private land area
    # geom_copy = geom.Clone()
    # geom_copy.Transform(trans_PL)
    # PL_lyr.SetSpatialFilter(geom_copy)
    # if PL_lyr.GetFeatureCount() > 0:
    #     PL = 1
    #     print('Point is in OG area')
    #     print("")
    # else:
    #     PL = 0
    #     print('Point is NOT in OG area')
    #     print("")
    #PL_lyr.SetSpatialFilter(None)
    OG, PL = 0, 0
    df.append([id, OG, PL, elevation, distance])
    PO_feat = PO_lyr.GetNextFeature()
PO_lyr.ResetReading()
print(df)
exit(0)


labels = list(('ID', 'Private',  'OldGrowth', 'Elevation', 'Road_Dist'))
df = pd.DataFrame.from_records(df, columns = labels)
df.round({'Private': 1, 'OLDGrowth': 1, 'Road_Dist': 2})
df = pd.melt(df, id_vars=['ID'], value_vars=['Private',  'OldGrowth',
'Elevation', 'Road_Dist'])
df.sort_values(by=['ID'])

df.to_csv("result.csv", sep='\t')




############################################################################
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)

