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
VRTtarget = "DOY319_Nov15"
shape = "L:/biogeo-lab/SAN_BioGeo/_SHARED_DATA/CL_MB/__TrainingData/Sample_ID_Landsat_asPoint.shp"
VRTimage = "E:/Baumann/CHACO/_Composite_Landsat8_2015/" + VRTtarget + "_VRT.vrt"
VRTmetrics = "E:/Baumann/CHACO/_Composite_Landsat8_2015/Metrics_Nov15_VRT.vrt"
VRTflags = "E:/Baumann/CHACO/_Composite_Landsat8_2015/" + VRTtarget + "_MetaInfo_VRT.vrt"
out_file = "L:/biogeo-lab/SAN_BioGeo/_SHARED_DATA/CL_MB/__TrainingData/" + VRTtarget + "_pxExtract.csv"
# data-type references
imagery = "E:/Baumann/CHACO/_Composite_Landsat8_2015/" + VRTtarget + "/Tile_x0_y0_999x999_2014-2015_CHACO_PBC_multiYear_Imagery.bsq"
metrics = "E:/Baumann/CHACO/_Composite_Landsat8_2015/Metrics_Nov15/Tile_x0_y0_999x999_2014-2015_CHACO_PBC_multiYear_Metrics.bsq"
flags = "E:/Baumann/CHACO/_Composite_Landsat8_2015/" + VRTtarget + "_MetaInfo/Tile_x0_y0_999x999_2014-2015_CHACO_PBC_multiYear_MetaFlags.bsq"
# ####################################### PROCESSING ########################################################## #
# Check what type of VRT it is --> Imagery, Metrics, or Flags
valueList = []
header = ["Point_ID",
          # Imagery
          "b1", "b2", "b3", "b4", "b5", "b6",
          # Metrics
          "b1mean", "b2mean", "b3mean", "b4mean", "b5mean", "b6mean",
          "b1median", "b2median", "b3median", "b4median", "b5median", "b6median",
          "b1STDV", "b2STDV", "b3STDV", "b4STDV", "b5STDV", "b6STDV",
          "b1Q25", "b2Q25", "b3Q25", "b4Q25", "b5Q25", "b6Q25",
          "b1Q50", "b2Q50", "b3Q50", "b4Q50", "b5Q50", "b6Q50",
          "b1Q75", "b2Q75", "b3Q75", "b4Q75", "b5Q75", "b6Q75",
          "b1Median25Q50", "b2Median25Q50", "b3Median25Q50", "b4Median25Q50", "b5Median25Q50", "b6Median25Q50",
          "b1Median50Q75", "b2Median50Q75", "b3Median50Q75", "b4Median50Q75", "b5Median50Q75", "b6Median50Q75",
          "b1Slope", "b2Slope", "b3Slope", "b4Slope", "b5Slope", "b6Slope",
          "b1RangeQ75Q25", "b2RangeQ75Q25", "b3RangeQ75Q25", "b4RangeQ75Q25", "b5RangeQ75Q25", "b6RangeQ75Q25",
          # Flags
          "DOY", "nClearObs", "Zenit", "Azimuth"]
valueList.append(header)

# Open the VRT-files
print("Open VRT")
img_open = gdal.Open(VRTimage, GA_ReadOnly)
bands_img = img_open.RasterCount
gt = img_open.GetGeoTransform()
pr = img_open.GetProjection()
metrics_open = gdal.Open(VRTmetrics, GA_ReadOnly)
bands_metrics = metrics_open.RasterCount
flags_open = gdal.Open(VRTflags, GA_ReadOnly)
bands_flags = [3, 6, 8, 9] # Manually choses: DOY, nClearObs, Zenit, Azimuth
# Open the reference-raster, to extract the data-types later
ref_img = gdal.Open(imagery, GA_ReadOnly)
ref_met = gdal.Open(metrics, GA_ReadOnly)
ref_flag = gdal.Open(flags, GA_ReadOnly)
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
    # Create list for the values of this feature, add Id-value
    valList = []
    id = feat.GetField("UniqueID")
    valList.append(id)
    print("Processing Point-ID ", id)
    # Build the geometry, and apply the coordinate transformation
    geom = feat.GetGeometryRef()
    geom.Transform(coordTrans)
    mx, my = geom.GetX(), geom.GetY()
    px = int((mx - gt[0]) / gt[1])
    py = int((my - gt[3]) / gt[5])
    # Get the raster value from the IMAGERY
    for b in range(bands_img):
        # Determine the datatype from the reference raster
        ref_rb = ref_img.GetRasterBand(b+1)
        dTypes = [[1,'b'], [2,'H'], [3,'h'], [4,'I'], [5,'i'],[6,'f'],[7,'d']]
        ref_dType = ref_rb.DataType
        for dT in dTypes:
            if dT[0] == ref_dType:
                band_dType = dT[1]
        # Now extract the value from the raster
        img_open_rb = img_open.GetRasterBand(b+1)
        structVar = img_open_rb.ReadRaster(px,py,1,1)
        Val = struct.unpack(band_dType, structVar)[0]
        valList.append(Val)
    # Get the raster value from the METRICS
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
    # Get the raster values from the METAINFO
    for b in bands_flags:
        # Determine the datatype from the reference raster
        ref_rb = ref_flag.GetRasterBand(b)
        dTypes = [[1,'b'], [2,'H'], [3,'h'], [4,'I'], [5,'i'],[6,'f'],[7,'d']]
        ref_dType = ref_rb.DataType
        for dT in dTypes:
            if dT[0] == ref_dType:
                band_dType = dT[1]
        # Now extract the value from the raster
        flags_open_rb = flags_open.GetRasterBand(b)
        structVar = flags_open_rb.ReadRaster(px,py,1,1)
        Val = struct.unpack(band_dType, structVar)[0]
        valList.append(Val)
    # Append the valList to the outputlist, go to next feature
    valueList.append(valList)
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