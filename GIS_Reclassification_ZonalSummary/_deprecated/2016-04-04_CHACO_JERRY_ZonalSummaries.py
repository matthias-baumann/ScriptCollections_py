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
    "D:/Matthias/Projects-and-Publications/Publications/Commented_manuscripts/2016_Jerry_ZonalSummaries_Chaco/SantiagoDelEstero_Cadaster_SAD69.shp"),'')
classification = gdal.Open(
    "D:/Matthias/Projects-and-Publications/Publications/Publications-submitted-in-review/2015_Baumann-etal_Chaco-LCLUC_Carbon/run12_classification_full_masked_clump-eliminate4px_reclass_V02.img",GA_ReadOnly)
classes = [[1, "F-F-F"],[4, "C-C-C"],[5, "P-P-P"],[10, "F-C-C"],[11, "F-P-P"],[12, "F-F-C"],[13, "F-F-P"],[14, "F-P-C"],[17, "Fs-Fs-Fs"],[20, "P-C-C"],[21, "P-P-C"]]
# ############################################################################################################# #
outFile = "D:/Matthias/Projects-and-Publications/Publications/Commented_manuscripts/2016_Jerry_ZonalSummaries_Chaco/SantiagoDelEstero_Cadaster_SAD69_summaries.csv"
# ############################################################################################################# #
outList = []
header = ["UniqueID", "PolygonArea_km", "F_1985_km2", "F_2000_km2", "F_2013_km2", "C_1985_km2", "C_2000_km2", "C_2013_km2", "P_1985_km2", "P_2000_km2", "P_2013_km2"]
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
# Create a geometry, calculate the area to append to the table, and apply the coordinate transformation
    geom = feat.GetGeometryRef()
    # Calculate the area of the polygon (coordinate system is in m2 - convert to km2)
    areakm2 = geom.GetArea() / 1000000
    vals.append(areakm2)
    # Transform (here not necessary, as the two files have the same coordinate system)
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
# Polygon has to be at least one pixel wide or long
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
        def ClassAreaSums(listRasterValues, inBuffArray):
            area = 0
            for value in listRasterValues:
                nr_px = np.count_nonzero(inBuffArray == value)
                sub_area = (nr_px*900)/1000000
                area = area + sub_area
            return area
    # [[1, "F-F-F"],[4, "C-C-C"],[5, "P-P-P"],[10, "F-C-C"],[11, "F-P-P"],[12, "F-F-C"],[13, "F-F-P"],[14, "F-P-C"],[17, "Fs-Fs-Fs"],[20, "P-C-C"],[21, "P-P-C"]]
        vals.append(ClassAreaSums([1,10,11,12,13,14,17],inBuff_array))
        vals.append(ClassAreaSums([1,12,13,17],inBuff_array))
        vals.append(ClassAreaSums([1,17],inBuff_array))
        vals.append(ClassAreaSums([4],inBuff_array))
        vals.append(ClassAreaSums([4,10,20],inBuff_array))
        vals.append(ClassAreaSums([4,10,12,14,20,21],inBuff_array))
        vals.append(ClassAreaSums([5,20,21],inBuff_array))
        vals.append(ClassAreaSums([5,11,14,21],inBuff_array))
        vals.append(ClassAreaSums([5,11,13],inBuff_array))
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
# Get the next feature
    outList.append(vals)
    feat = lyr.GetNextFeature()
lyr.ResetReading()
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