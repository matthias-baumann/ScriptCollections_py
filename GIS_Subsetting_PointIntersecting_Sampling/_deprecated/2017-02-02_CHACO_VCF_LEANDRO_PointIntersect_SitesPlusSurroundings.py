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
shape = "B:/Projects-and-Publications/Publications/Publications-in-preparation/Macci-etal_Percent-tree-cover_Chaco/sites_pasanoa_20170202_SAD69.shp"
#VRTimage = "E:/Baumann/CHACO/_Composite_Landsat8_2015/" + VRTtarget + "_VRT.vrt"
VRTmetrics = "E:/Baumann/CHACO/_Composite_Landsat8_2015/Metrics_Nov15_VRT.vrt"
SAR_vv = "G:/CHACO/_COMPOSITING/S1_extracted/_Sentinel-1_vv.vrt"
#SAR_hv = "G:/CHACO/_COMPOSITING/S1_extracted/_Sentinel-1_hv.vrt"
#VRTflags = "E:/Baumann/CHACO/_Composite_Landsat8_2015/" + VRTtarget + "_MetaInfo_VRT.vrt"
out_file = "B:/Projects-and-Publications/Publications/Publications-in-preparation/Macci-etal_Percent-tree-cover_Chaco/sites_pasanoa_20170202_SAD69_values_SARvv_20170202_3x3plot.csv"
# data-type references
#imagery = "E:/Baumann/CHACO/_Composite_Landsat8_2015/DOY319_Nov15/Tile_x0_y0_999x999_2014-2015_CHACO_PBC_multiYear_Imagery.bsq"
metrics = "E:/Baumann/CHACO/_Composite_Landsat8_2015/Metrics_Nov15/Tile_x0_y0_999x999_2014-2015_CHACO_PBC_multiYear_Metrics.bsq"
SARref = "G:/CHACO/_COMPOSITING/S1_extracted/S1A_IW_GRDH_1SDV_20150430T092634_20150430T092659_005711_00754A_E2BA.tif"
# ####################################### PROCESSING ########################################################## #
# Check what type of VRT it is --> Imagery, Metrics, or Flags
valueList = []
header = ["Site_ID","Site_Name","Pixel",
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
          "SAR"]
valueList.append(header)

# Open the VRT-files
print("Open VRT")
metrics_open = gdal.Open(VRTmetrics, GA_ReadOnly)
gt = metrics_open.GetGeoTransform()
pr = metrics_open.GetProjection()
bands_metrics = metrics_open.RasterCount
SARvv_open = gdal.Open(SAR_vv, GA_ReadOnly)
ref_met = gdal.Open(metrics, GA_ReadOnly)
ref_SAR = gdal.Open(SARref, GA_ReadOnly)
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
# Get fields from the site
    id = feat.GetField("ID")
    print("Processing Point-ID ", id)
    tc = feat.GetField("site")
# Build the geometry, and apply the coordinate transformation
    geom = feat.GetGeometryRef()
    geom.Transform(coordTrans)
    mx, my = geom.GetX(), geom.GetY()
    px = int((mx - gt[0]) / gt[1])
    py = int((my - gt[3]) / gt[5])
# Get the value at the center pixel and the surrounding --> tupel = [[type, x_off, y_off],...], loop through it
    whichPX = [["1", 10, 10], ["2", 0, 10], ["3", 10, 0], ["4", -10, 0], ["5", 0, 0], ["6", 10, 0], ["7", -10, -10], ["8", 0, -10], ["9", 10, 10]]
    for combo in whichPX:
        valList = []
        valList.append(id)
        valList.append(tc)
# Get the values for the combo
        valList.append(combo[0])
        new_px = px + combo[1]
        new_py = py + combo[2]
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
            structVar = metrics_open_rb.ReadRaster(new_px,new_py,1,1)
            Val = struct.unpack(band_dType, structVar)[0]
            valList.append(Val)
    # Get the raster values from the SAR
    # Determine the datatype from the reference raster
        ref_rb = ref_SAR.GetRasterBand(1)
        dTypes = [[1,'b'], [2,'H'], [3,'h'], [4,'I'], [5,'i'],[6,'f'],[7,'d']]
        ref_dType = ref_rb.DataType
        for dT in dTypes:
            if dT[0] == ref_dType:
                band_dType = dT[1]
    # Now extract the value from the raster
        SAR_open_rb = SARvv_open.GetRasterBand(1)
        structVar = SAR_open_rb.ReadRaster(new_px,new_py,1,1)
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