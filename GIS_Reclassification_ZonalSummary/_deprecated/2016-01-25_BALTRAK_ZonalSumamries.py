# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import csv
import time
import gdal, osr, ogr
from ZumbaTools._Vector_Tools import *
from gdalconst import *
import numpy as np
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ####################################### FUNCTIONS, FOLDER PATHS AND BASIC VARIABLES ######################### #
shape = "Y:/Baltrak/00_SHP/AdminBoundaries_StudyArea_large_20151107.shp"
classification = "Y:/Baltrak/03_Classification/02_NewExtent/ClassRuns/Run09_ClumpSieve_10px_masked.tif"
classes = [[1, "F-F-F"],[2, "Wetlands"],[3, "Water"],[4, "Other"],[5, "C-C-C"],[6, "C-G-G"],[7, "C-C-G"],[8, "G-G-G"],
           [9, "G-G-C"],[10, "G-C-C"],[11, "C-G-C"],[12, "F-F-NF"],[13, "F-NF-NF"],[14, "G-C-G"],[15, "Wet-Agro"]]
outFile = "Y:/Baltrak/03_Classification/02_NewExtent/ClassRuns/Run09_ClumpSieve_10px_masked_ZonalSummaries.csv"
ZoneField = "UniqueID"
# Create Outputlist for values, then build header for the csv file
valueList = []
header = [ZoneField]
for cl in classes:
    header.append(cl[1])
valueList.append(header)
# Load drivers etc.
drvV = ogr.GetDriverByName('ESRI Shapefile')
drvR = gdal.GetDriverByName('HFA')
drvMemV = ogr.GetDriverByName('Memory')
drvMemR = gdal.GetDriverByName('MEM')
# Open the Shapefile
sh_open = ogr.Open(shape, 1)
lyr = sh_open.GetLayer()
pol_srs = lyr.GetSpatialRef()
# Open the raster
ras_open = gdal.Open(classification, GA_ReadOnly)
gt = ras_open.GetGeoTransform()
pr = ras_open.GetProjection()
cols = ras_open.RasterXSize
rows = ras_open.RasterYSize
# Build the coordinate transformation
ras_srs = ras_open.GetProjection()
target_SR = osr.SpatialReference()
target_SR.ImportFromWkt(ras_srs)
transform = osr.CoordinateTransformation(pol_srs, target_SR)
# Loop through features
print("")
feat = lyr.GetNextFeature()
while feat:
# Get the Unique-ID for the print-statement
    id = feat.GetField(ZoneField)
    print("Processing polygon with Unique-ID:", id)
    vals = [id]
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
    gdal.ReprojectImage(ras_open, rasMem, pr, shpMem_asRaster.GetProjection(), gdal.GRA_NearestNeighbour)
    rasMem_array = np.array(rasMem.GetRasterBand(1).ReadAsArray())
# Now mask out the areas outside the buffer (shpMem_array = 0)
    inBuff_array = rasMem_array
    np.putmask(inBuff_array, shpMem_array == 0, 999)
# Loop through each of the classes, extract the number of pixels, convert pixels into km2
    for cl in classes:
        val = cl[0]
        #nr_px = (inBuff_array == val).sum())
        nr_px = np.count_nonzero(inBuff_array == val)
        vals.append(nr_px)
# Destroy all memory elements
    shpMem.Destroy()
    shpMem_feat.Destroy()
    shpMem_asRaster = None
    shpMem_asRaster = None
    shpMem_array = None
    rasMem = None
    rasMem_array = None
    inBuff_array = None
# Get the next feature
    valueList.append(vals)
    feat = lyr.GetNextFeature()
lyr.ResetReading()
# Write output
with open(outFile, "w") as theFile:
    csv.register_dialect("custom", delimiter = ",", skipinitialspace = True, lineterminator = '\n')
    writer = csv.writer(theFile, dialect = "custom")
    writer
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