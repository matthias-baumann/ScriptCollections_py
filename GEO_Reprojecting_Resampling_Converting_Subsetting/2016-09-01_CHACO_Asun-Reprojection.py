# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import gdal, osr, ogr
from gdalconst import *
import numpy as np
from ZumbaTools._Raster_Tools import *
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " +  starttime)
print("")
# ####################################### DRIVERS AND FOLDER-PATHS ############################################ #
drvR = gdal.GetDriverByName('GTiff')
drvMemR = gdal.GetDriverByName('MEM')
drvMemV = ogr.GetDriverByName('Memory')
drvV = ogr.GetDriverByName('ESRI Shapefile')
outputFolder = "L:/biogeo-lab/SAN_BioGeo/_SHARED_DATA/ASP_MB/Converted/"
inputFolder = "L:/biogeo-lab/SAN_BioGeo/_SHARED_DATA/ASP_MB/Matthias_thanks/"
pr = gdal.Open("L:/biogeo-lab/SAN_BioGeo/_SHARED_DATA/ASP_MB/1985_composite.bsq", GA_ReadOnly).GetProjection()
# ####################################### FUNCTIONS ########################################################### #
def ReprojectRaster(inRaster, outProj):
# (1) Build the coordinate transformation for the geotransform
    inPR = osr.SpatialReference()
    inPR.ImportFromWkt(inRaster.GetProjection())
    outPR = osr.SpatialReference()
    outPR.ImportFromWkt(outProj)
    transform = osr.CoordinateTransformation(inPR, outPR)
# (2) Build the output Geotransform, pixelsize and imagesize
    inGT = inRaster.GetGeoTransform()
    cols = inRaster.RasterXSize
    rows = inRaster.RasterYSize
    ulx, uly, ulz = transform.TransformPoint(inGT[0], inGT[3])
    lrx, lry, lrz = transform.TransformPoint(inGT[0] + inGT[1] * cols, inGT[3] + inGT[5] * rows)
    pxSize = int(lrx - ulx) / cols
    newcols = int((lrx - ulx)/ pxSize)
    newrows = int((uly - lry)/ pxSize)
    outGT = (ulx, pxSize, inGT[2], uly, inGT[4], -pxSize)
# (3) Create the new file and reproject
    dtype = inRaster.GetRasterBand(1).DataType
    outfile = drvMemR.Create('', newcols, newrows, 1, dtype)
    outfile.SetProjection(outProj)
    outfile.SetGeoTransform(outGT)
    res = gdal.ReprojectImage(inRaster, outfile, inPR.ExportToWkt(), outProj, gdal.GRA_NearestNeighbour)
    return outfile
def ReprojectShape(inShape, outProj, outname):
# Open the layer of the input shapefile
    shp = drvMemV.CopyDataSource(ogr.Open(inShape),'')
    lyr = shp.GetLayer()
# Build the coordinate Transformation
    inPR = lyr.GetSpatialRef()
    outPR = osr.SpatialReference()
    outPR.ImportFromWkt(outProj)
    transform = osr.CoordinateTransformation(inPR, outPR)
# Create the output-SHP and LYR, get geometry type first
    feat = lyr.GetNextFeature()
    geom = feat.GetGeometryRef()
    geomType = geom.GetGeometryType()
    lyr.ResetReading()
    outSHP = drvV.CreateDataSource(outname)
    outLYR = outSHP.CreateLayer('outSHP', outPR, geom_type=geomType)
# Create all fields in the new shp-file that we created before
    inLayerDefn = lyr.GetLayerDefn()
    for i in range(0, inLayerDefn.GetFieldCount()):
        fieldDefn = inLayerDefn.GetFieldDefn(i)
        outLYR.CreateField(fieldDefn)
# get the output layer's feature definition
    outLYRDefn = outLYR.GetLayerDefn()
# Now loop through the features from the inSHP, transform geometries, add to new SHP and also take the values in the attributes
    feat = lyr.GetNextFeature()
    while feat:
        geom = feat.GetGeometryRef()
        geom.Transform(transform)
        outFeat = ogr.Feature(outLYRDefn)
        outFeat.SetGeometry(geom)
        for i in range(0, outLYRDefn.GetFieldCount()):
            outFeat.SetField(outLYRDefn.GetFieldDefn(i).GetNameRef(), feat.GetField(i))
        outLYR.CreateFeature(outFeat)
# Destroy/Close the features and get next input-feature
        outFeat.Destroy()
        feat.Destroy()
        feat = lyr.GetNextFeature()
# Close the shapefiles, return the output shapefile
    shp.Destroy()
    outSHP.Destroy()
    return outSHP
rasList_grid = [file for file in os.listdir(inputFolder) if file.find(".") < 0]
rasList_tiff = [file for file in os.listdir(inputFolder) if file.endswith(".tif")]
shpList = [file for file in os.listdir(inputFolder) if file.endswith(".shp")]
# (1) Convert SHP-Files
for shp in shpList:
    print(shp)
    input = inputFolder + shp
    output = outputFolder + shp
    output = output.replace(".shp", "_SAEAC.shp")
    if not os.path.exists(output):
        outSHP = ReprojectShape(input, pr, output)
    else:
        print("--> already processed. Skipping...")
# (2) Comvert GRID-files
for grid in rasList_grid:
    print(grid)
    input = gdal.Open(inputFolder + grid, GA_ReadOnly)
    output = outputFolder + grid + "_SAEAC.tif"
    if not os.path.exists(output):
        outFile = ReprojectRaster(input, pr)
        CopyMEMtoDisk(outFile, output)
    else:
        print("--> already processed. Skipping...")
# (3) Convert tiff layers
for tiff in rasList_tiff:
    print(tiff)
    input = gdal.Open(inputFolder + tiff, GA_ReadOnly)
    output = outputFolder + tiff
    output = output.replace(".tif", "_SAEAC.tif")
    if not os.path.exists(output):
        outFile = ReprojectRaster(input, pr)
        CopyMEMtoDisk(outFile, output)
    else:
        print("--> already processed. Skipping...")

# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")