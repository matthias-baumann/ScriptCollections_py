# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import gdal
import ogr, osr
from gdalconst import *
import struct
import csv
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ####################################### HARD-CODED FOLDERS AND FILES ######################################## #
#VRTtarget = "DOY319_Nov15"
#shape = "B:/Projects-and-Publications/Publications/Publications-in-preparation/baumann-etal_Pecent-TreeShrubCover_Chaco/__Analysis_and_Scripts/_shapeFiles_Samples/Sample_ID_Landsat_AsPoint.shp"
shape = "B:/Projects-and-Publications/Publications/Publications-in-preparation/baumann-etal_Pecent-TreeShrubCover_Chaco/__Analysis_and_Scripts/_shapeFiles_Samples/RandomPoints_Squares_Neighbors_AsPoint.shp"
VRTmetrics = "E:/Baumann/CHACO/_Composite_Landsat8_2015/Metrics_Nov15_VRT.vrt"
S1mean = "E:/Baumann/CHACO/Sentinel-1_HH_mean_composite.vrt"
S1max = "E:/Baumann/CHACO/Sentinel-1_HH_max_composite.vrt"
#out_file = "B:/Projects-and-Publications/Publications/Publications-in-preparation/baumann-etal_Pecent-TreeShrubCover_Chaco/__Analysis_and_Scripts/_Version_Landsat_plus_Sentinel/Sample_ID_Landsat_AsPoint_values_20170508.csv"
out_file = "B:/Projects-and-Publications/Publications/Publications-in-preparation/baumann-etal_Pecent-TreeShrubCover_Chaco/__Analysis_and_Scripts/_Version_Landsat_plus_Sentinel/RandomPoints_Squares_Neighbors_AsPoint_values_20170508.csv"
# data-type references
metrics = "E:/Baumann/CHACO/_Composite_Landsat8_2015/Metrics_Nov15/Tile_x0_y0_999x999_2014-2015_CHACO_PBC_multiYear_Metrics.bsq"
mean = "E:/Baumann/CHACO/_Composite_Sentinel1_2015_new/HH_mean/Tile_x0_y54999_999x1000_2014-2015_CHACO.tif"
max = "E:/Baumann/CHACO/_Composite_Sentinel1_2015_new/HH_max/Tile_x0_y54999_999x1000_2014-2015_CHACO.tif"
# ####################################### PROCESSING ########################################################## #
# Check what type of VRT it is --> Imagery, Metrics, or Flags
valueList = []
header = ["Point_ID","TC","SC",
          "MEAN_band_1", "MEAN_band_2", "MEAN_band_3", "MEAN_band_4", "MEAN_band_5", "MEAN_band_7",
          "MEDIAN_band_1", "MEDIAN_band_2", "MEDIAN_band_3", "MEDIAN_band_4", "MEDIAN_band_5", "MEDIAN_band_7",
          "STDV_band_1", "STDV_band_2", "STDV_band_3", "STDV_band_4", "STDV_band_5", "STDV_band_7",
          "Q25_band_1", "Q25_band_2", "Q25_band_3", "Q25_band_4", "Q25_band_5", "Q25_band_7",
          "Q50_band_1", "Q50_band_2", "Q50_band_3", "Q50_band_4", "Q50_band_5", "Q50_band_7",
          "Q75_band_1", "Q75_band_2", "Q75_band_3", "Q75_band_4", "Q75_band_5", "Q75_band_7",
          "MEDIAN25Q50_band_1", "MEDIAN25Q50_band_2", "MEDIAN25Q50_band_3", "MEDIAN25Q50_band_4", "MEDIAN25Q50_band_5", "MEDIAN25Q50_band_7",
          "MEDIAN50Q75_band_1", "MEDIAN50Q75_band_2", "MEDIAN50Q75_band_3", "MEDIAN50Q75_band_4", "MEDIAN50Q75_band_5", "MEDIAN50Q75_band_7",
          "SLOPE_band_1", "SLOPE_band_2", "SLOPE_band_3", "SLOPE_band_4", "SLOPE_band_5", "SLOPE_band_7",
          "RANGE_Q75_Q25_band_1", "RANGE_Q75_Q25_band_2", "RANGE_Q75_Q25_band_3", "RANGE_Q75_Q25_band_4", "RANGE_Q75_Q25_band_5", "RANGE_Q75_Q25_band_7",
          "S1_mean", "S1_max"]
valueList.append(header)

# Open the VRT-files
print("Open VRT")
metrics_open = gdal.Open(VRTmetrics, GA_ReadOnly)
gt = metrics_open.GetGeoTransform()
pr = metrics_open.GetProjection()
bands_metrics = metrics_open.RasterCount
S1mean_open = gdal.Open(S1mean, GA_ReadOnly)
S1max_open = gdal.Open(S1max, GA_ReadOnly)
ref_met = gdal.Open(metrics, GA_ReadOnly)
ref_S1mean = gdal.Open(mean, GA_ReadOnly)
ref_S1max = gdal.Open(max, GA_ReadOnly)
# Open the shapefile and build coordinate transformation
print("Open shp-file")
ds_ogr = ogr.Open(shape, 1)
lyr = ds_ogr.GetLayer()
target_SR = osr.SpatialReference()
target_SR.ImportFromWkt(pr)
source_SR = lyr.GetSpatialRef()
coordTrans = osr.CoordinateTransformation(source_SR, target_SR)
# Loop through each feature and extract the values
feat = lyr.GetNextFeature()
while feat:
# Check if observation should be used
    check = feat.GetField("use_YN")
    if check == 1:
# Create list for the values of this feature, add Id-value
        valList = []
        id = feat.GetField("ID")
        valList.append(id)
        print("Processing Point-ID ", id)
        tc = feat.GetField("TCperc")
        valList.append(tc)
        sc = feat.GetField("SCperc")
        valList.append(sc)
# Build the geometry, and apply the coordinate transformation
        geom = feat.GetGeometryRef()
        geom.Transform(coordTrans)
        mx, my = geom.GetX(), geom.GetY()
        px = int((mx - gt[0]) / gt[1])
        py = int((my - gt[3]) / gt[5])
# Extract the values from the Landsat-metrics
        for b in range(bands_metrics):
            # Determine the datatype from the reference raster
            ref_rb = ref_met.GetRasterBand(b+1)
            dTypes = [[1,'b'], [2,'H'], [3,'h'], [4,'I'], [5,'i'],[6,'f'],[7,'d']]
            ref_dType = ref_rb.DataType
            for dT in dTypes:
                if dT[0] == ref_dType:
                    band_dType = dT[1]
            # Now extract the value from the raster
            metrics_open_rb = metrics_open.GetRasterBand(b+1)
            structVar = metrics_open_rb.ReadRaster(px,py,1,1)
            Val = struct.unpack(band_dType, structVar)[0]
            valList.append(Val)
# Get the Sentinel-Mean data
        ref_S1mean_rb = ref_S1mean.GetRasterBand(1)
        dTypes = [[1,'b'], [2,'H'], [3,'h'], [4,'I'], [5,'i'],[6,'f'],[7,'d']]
        ref_dType = ref_S1mean_rb.DataType
        for dT in dTypes:
            if dT[0] == ref_dType:
                band_dType = dT[1]
        S1mean_open_rb = S1mean_open.GetRasterBand(1)
        structVar = S1mean_open_rb.ReadRaster(px,py,1,1)
        Val = struct.unpack(band_dType, structVar)[0]
        valList.append(Val)
# Get the Sentinel-max data
        ref_S1max_rb = ref_S1max.GetRasterBand(1)
        dTypes = [[1,'b'], [2,'H'], [3,'h'], [4,'I'], [5,'i'],[6,'f'],[7,'d']]
        ref_dType = ref_S1max_rb.DataType
        for dT in dTypes:
            if dT[0] == ref_dType:
                band_dType = dT[1]
        S1max_open_rb = S1max_open.GetRasterBand(1)
        structVar = S1max_open_rb.ReadRaster(px,py,1,1)
        Val = struct.unpack(band_dType, structVar)[0]
        valList.append(Val)
# Append the valList to the outputlist, go to next feature
        valueList.append(valList)
        feat = lyr.GetNextFeature()
    else:
        feat = lyr.GetNextFeature()
# Reset layer
lyr.ResetReading()
# Write the output-file
print("Write output")
with open(out_file, "w") as theFile:
    csv.register_dialect("custom", delimiter = ",", skipinitialspace = True, lineterminator = '\n')
    writer = csv.writer(theFile, dialect = "custom")
    for element in valueList:
        writer.writerow(element)
# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")