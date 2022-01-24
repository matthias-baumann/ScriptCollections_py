# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
from osgeo import ogr, gdal, osr
import baumiTools as bt
import random
import os
import struct
os.environ['PROJ_LIB'] = "C:/Users/baumamat/.conda/envs/py38/Library/share/proj"
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " +  starttime)
print("")
# ####################################### DRIVERS AND FOLDER-PATHS ############################################ #
drvV = ogr.GetDriverByName('ESRI Shapefile')
drvMemV = ogr.GetDriverByName('Memory')
workFolder = "L:/_SHARED_DATA/MB_TaKa/Tian Validation/"
dryForests = bt.baumiVT.CopyToMem(workFolder + "Polygons/Polygons_Merged_Final.shp")
raster = gdal.Open(workFolder + "y1930/Tian_1930.tif")
rb = raster.GetRasterBand(1)
rasdType = bt.baumiRT.GetDataTypeHexaDec(rb.DataType)
outPols = workFolder + "Tian_Vali_PixelPolygons.shp"
outPoints = workFolder + "Tian_Vali_Pixels.shp"
nSamples = 500

# ####################################### PROGRAMMING ######################################################### #
# (0) GET PROPERTIES FROM INPUT FILES, CREATE TRANSFORMATIONS; ETC.
# Properties
dryLYR = dryForests.GetLayer()
outPR = dryLYR.GetSpatialRef()
outPR.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
inPR = osr.SpatialReference()
inPR.ImportFromWkt(raster.GetProjection())
inPR.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
inGT = raster.GetGeoTransform()
cols = raster.RasterXSize
rows = raster.RasterYSize
# PR-Conversion
cT = osr.CoordinateTransformation(inPR, outPR)
cT2 = osr.CoordinateTransformation(outPR, inPR)

# (1) CREATE THE OUTPUT DATASET
# Points
points = drvV.CreateDataSource(outPoints)
pointsLYR = points.CreateLayer('', outPR, geom_type=ogr.wkbPoint)
IDfield = ogr.FieldDefn('ID', ogr.OFTInteger)
pointsLYR.CreateField(IDfield)
FCfield = ogr.FieldDefn('FC', ogr.OFTReal)
pointsLYR.CreateField(FCfield)
# Polygons
polygons = drvV.CreateDataSource(outPols)
polygonsLYR = polygons.CreateLayer('', outPR, geom_type=ogr.wkbPolygon)
IDfield = ogr.FieldDefn('ID', ogr.OFTInteger)
polygonsLYR.CreateField(IDfield)
FCfield = ogr.FieldDefn('FC', ogr.OFTReal)
polygonsLYR.CreateField(FCfield)

# (2) ADD NEW POINTS/POLYGONS TO THE SHAPEFILE UNTIL nSAMPLES IS REACHED
nPoints = 0
idCount = 1
while nPoints < nSamples:
	# Create random point as a center of one pixel
	xPX = random.randint(0, cols)
	#xPX = 119
	yPX = random.randint(0, rows)
	#yPX = 230
	xPX_geo = inGT[0] + xPX * inGT[1] + inGT[1]*0.5
	yPX_geo = inGT[3] + yPX * inGT[5] + inGT[5]*0.5
	geom = ogr.Geometry(ogr.wkbPoint)
	geom.AddPoint(xPX_geo, yPX_geo)
	geom.AssignSpatialReference(inPR)
	#bt.baumiVT.SaveGEOMtoFile(geom, "D:/1.shp")
	# Check if the point lies inside the polygon
	geom_cl = geom.Clone()
	geom_cl.Transform(cT)
	dryLYR.SetSpatialFilter(geom_cl)
	count = dryLYR.GetFeatureCount()
	# Check if the poit is at least 3 pixels away from previously sampled points
	geom_buff = geom_cl.Buffer(16000)
	pointsLYR.SetSpatialFilter(geom_buff)
	count2 = pointsLYR.GetFeatureCount()
	if count == 1 and count2 == 0:
		# If yes, then draw the polygon
		xPX_geo_tr = geom_cl.GetX()
		yPX_geo_tr = geom_cl.GetY()
		ring = ogr.Geometry(ogr.wkbLinearRing)
		ring.AddPoint(xPX_geo_tr - 4000, yPX_geo_tr + 4000)
		ring.AddPoint(xPX_geo_tr - 4000, yPX_geo_tr - 4000)
		ring.AddPoint(xPX_geo_tr + 4000, yPX_geo_tr - 4000)
		ring.AddPoint(xPX_geo_tr + 4000, yPX_geo_tr + 4000)
		ring.AddPoint(xPX_geo_tr - 4000, yPX_geo_tr + 4000)
		poly = ogr.Geometry(ogr.wkbPolygon)
		poly.AddGeometry(ring)
		poly.AssignSpatialReference(outPR)
		#bt.baumiVT.SaveGEOMtoFile(poly, "D:/2.shp")
		# Get the raster value from the Tian data and add to shapefile
		structVar = rb.ReadRaster(xPX, yPX, 1, 1)
		Val = round(struct.unpack(rasdType, structVar)[0], 6)
		# Add the polygon and point to the shapefiles to the shapefiles
		# Point
		featOut_pnt = ogr.Feature(pointsLYR.GetLayerDefn())
		featOut_pnt.SetGeometry(geom_cl)
		featOut_pnt.SetField('ID', idCount)
		featOut_pnt.SetField('FC', Val)
		pointsLYR.CreateFeature(featOut_pnt)
		# Polygon
		featOut_pol = ogr.Feature(polygonsLYR.GetLayerDefn())
		featOut_pol.SetGeometry(poly)
		featOut_pol.SetField('ID', idCount)
		featOut_pol.SetField('FC', Val)
		polygonsLYR.CreateFeature(featOut_pol)
		# Increase counters for variable and IDs
		nPoints += 1
		idCount += 1
# Write the shapefiles to drive
#bt.baumiVT.CopySHPDisk(points, outPoints)
#bt.baumiVT.CopySHPDisk(polygons, outPols)

# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")