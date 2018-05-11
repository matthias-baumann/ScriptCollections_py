# ############################################################################################################# #
import os
import time
import gdal, osr, ogr
from ZumbaTools._Vector_Tools import *
import numpy as np
import csv
from gdalconst import *
# ############################################################################################################# #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ############################################################################################################# #
drvV = ogr.GetDriverByName('ESRI Shapefile')
drvR = gdal.GetDriverByName('HFA')
drvMemV = ogr.GetDriverByName('Memory')
drvMemR = gdal.GetDriverByName('MEM')
shape = drvMemV.CopyDataSource(ogr.Open(
    "D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/Marinaro-etal_Avance-de-la-frontera-agropecuaria-y-delimitación-de-lotes-en-el-Chaco-Seco/DEPTOS_DEMARCADOS_CHACO.shp"),'')
classification = gdal.Open(
    "D:/Matthias/Projects-and-Publications/Projects_Active/PASANOA/baumann-etal_LandCoverMaps_SingleYears/run12_classification_full_masked_clump-eliminate4px_reclass_V02.img",GA_ReadOnly)
classes = [[1, "F-F-F"],[4, "C-C-C"],[5, "P-P-P"],[10, "F-C-C"],[11, "F-P-P"],[12, "F-F-C"],[13, "F-F-P"],[14, "F-P-C"],[17, "Fs-Fs-Fs"],[20, "P-C-C"],[21, "P-P-C"]]
# ############################################################################################################# #
outFile = "D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/Marinaro-etal_Avance-de-la-frontera-agropecuaria-y-delimitación-de-lotes-en-el-Chaco-Seco/DEPTOS_DEMARCADOS_CHACO_Summary.csv"
# ############################################################################################################# #
outList = []
header = ["UniqueID", "PolygonArea_km", "F-F-F_km2", "C-C-C_km2", "P-P-P_km2", "F-C-C_km2", "F-P-P_km2", "F-F-C_km2", "F-F-P_km2", "F-P-C_km2", "Fs-Fs-Fs_km2", "P-C-C_km2", "P-P-C_km2"]
outList.append(header)

# (2) LOOP THROUGH EACH OF THE FEATURES IN THE SHAPEFILE AND GET THE AREAS OF EACH CLASS
lyr = shape.GetLayer()
gt = classification.GetGeoTransform()
pr = classification.GetProjection()
cols = classification.RasterXSize
rows = classification.RasterYSize
# Build the coordinate transformation
pol_srs = lyr.GetSpatialRef()
ras_srs = classification.GetProjection()
target_SR = osr.SpatialReference()
target_SR.ImportFromWkt(ras_srs)
transform = osr.CoordinateTransformation(pol_srs, target_SR)
# Loop through features
print("")
feat = lyr.GetNextFeature()
while feat:
    vals = []
# Get the Unique-ID for the print-statement
    id = feat.GetField("UniqueID")
    vals.append(id)
    print("Processing polygon with Unique-ID:", id)
# Get the area information from the Area-Field
    vals.append(feat.GetField("Area_km2"))
# Create a geometry and apply the coordinate transformation
    geom = feat.GetGeometryRef()
    geom.Transform(transform)
# Create new SHP-file in memory to which we copy the geometry
    shpMem = drvMemV.CreateDataSource('')
    shpMem_lyr = shpMem.CreateLayer('shpMem', target_SR, geom_type = ogr.wkbMultiPolygon)
    shpMem_lyr_defn = shpMem_lyr.GetLayerDefn()
    shpMem_feat = ogr.Feature(shpMem_lyr_defn)
    shpMem_feat.SetGeometry(geom.Clone())
    shpMem_lyr.CreateFeature(shpMem_feat)
# Load new SHP-file into array
    x_min, x_max, y_min, y_max = shpMem_lyr.GetExtent()
    x_res = int((x_max - x_min) / 30) # 30 here is because of the Landsat resolution
    y_res = int((y_max - y_min) / 30)
    if x_res > 0 and y_res > 0:
        shpMem_asRaster = drvMemR.Create('', x_res, y_res, gdal.GDT_Byte)
        shpMem_asRaster.SetProjection(ras_srs)
        shpMem_asRaster.SetGeoTransform((x_min, 30, 0, y_max, 0, -30))
        shpMem_asRaster_b = shpMem_asRaster.GetRasterBand(1)
        shpMem_asRaster_b.SetNoDataValue(255)
        gdal.RasterizeLayer(shpMem_asRaster, [1], shpMem_lyr, burn_values=[1])
        shpMem_array = np.array(shpMem_asRaster_b.ReadAsArray())
    # Subset the classification raster and load it into the array
        rasMem = drvMemR.Create('', shpMem_asRaster.RasterXSize, shpMem_asRaster.RasterYSize, 1, gdal.GDT_Byte)
        rasMem.SetGeoTransform(shpMem_asRaster.GetGeoTransform())
        rasMem.SetProjection(shpMem_asRaster.GetProjection())
        gdal.ReprojectImage(classification, rasMem, pr, shpMem_asRaster.GetProjection(), gdal.GRA_NearestNeighbour)
        rasMem_array = np.array(rasMem.GetRasterBand(1).ReadAsArray())
    # Now mask out the areas outside the buffer (shpMem_array = 0)
        inBuff_array = rasMem_array
        np.putmask(inBuff_array, shpMem_array == 0, 999)
    # Loop through each of the classes, extract the number of pixels, convert pixels into km2
        def ClassArea(rasterValue, inBuffArray):
            nr_px = np.count_nonzero(inBuffArray == rasterValue)
            area = (nr_px*900)/1000000
            return area
        vals.append(ClassArea(1,inBuff_array))
        vals.append(ClassArea(4,inBuff_array))
        vals.append(ClassArea(5,inBuff_array))
        vals.append(ClassArea(10,inBuff_array))
        vals.append(ClassArea(11,inBuff_array))
        vals.append(ClassArea(12,inBuff_array))
        vals.append(ClassArea(13,inBuff_array))
        vals.append(ClassArea(14,inBuff_array))
        vals.append(ClassArea(17,inBuff_array))
        vals.append(ClassArea(20,inBuff_array))
        vals.append(ClassArea(21,inBuff_array))
    # Get the next feature
        feat = lyr.GetNextFeature()
    else:
        vals.append("NA")
        vals.append("NA")
        vals.append("NA")
        vals.append("NA")
        vals.append("NA")
        vals.append("NA")
        vals.append("NA")
        vals.append("NA")
        vals.append("NA")
        vals.append("NA")
        vals.append("NA")
        feat = lyr.GetNextFeature()
    outList.append(vals)
# Write output
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