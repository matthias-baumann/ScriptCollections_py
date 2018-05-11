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
shape = "D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/baumann-etal_LandUseChange-Wilderness_Kostanay-KZ/Shapefiles/AdminRegions_3Oblasts.shp"
rasFolder = "D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/baumann-etal_LandUseChange-Wilderness_Kostanay-KZ/05_Wilderness_LivestockDisaggreg_InputData/_WildernessRuns/20160926_Run05/"
inRas = rasFolder + "wild15_minTwo.tif"
outFile = "D:/Users/baumamat/Desktop/wild15_minTwo.csv"
ZoneField = "UniqueID"
field = "wild90_sum"
# Create Outputlist for values, then build header for the csv file
valueList = []
header = [ZoneField, field]
valueList.append(header)
# Load drivers etc.
drvV = ogr.GetDriverByName('ESRI Shapefile')
drvR = gdal.GetDriverByName('GTiff')
drvMemV = ogr.GetDriverByName('Memory')
drvMemR = gdal.GetDriverByName('MEM')
# Open the Shapefile
sh_open = ogr.Open(shape, 1)
lyr = sh_open.GetLayer()
pol_srs = lyr.GetSpatialRef()
# Open the raster
ras_open = gdal.Open(inRas, GA_ReadOnly)
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
    masked = np.where((shpMem_array == 1), rasMem_array, 999)
# Loop through each of the classes, extract the number of pixels, convert pixels into km2

    valall = len(masked[masked < 999])
    val01 = len(masked[masked == 1])
    ratio = val01 / valall
    vals.append(ratio)

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