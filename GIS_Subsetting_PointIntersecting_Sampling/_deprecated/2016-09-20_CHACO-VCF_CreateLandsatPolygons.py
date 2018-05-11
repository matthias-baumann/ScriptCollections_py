# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import ogr
#from ZumbaTools._Raster_Tools import *
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " +  starttime)
print("")
# ####################################### DRIVERS AND FOLDER-PATHS ############################################ #
drvV = ogr.GetDriverByName('ESRI Shapefile')
drvMemV = ogr.GetDriverByName('Memory')
points = "F:/Projects-and-Publications/Publications/Publications-in-preparation/Macci-etal_Percent-tree-cover_Chaco/_BirdData_InclDigitization/sitios91x9_hendrik_20160915_AsPoints_SAD69.shp"
outfile = "F:/Projects-and-Publications/Publications/Publications-in-preparation/Macci-etal_Percent-tree-cover_Chaco/_BirdData_InclDigitization/sitios91x9_hendrik_20160915_AsPoints_SAD69_Squares_Neighbors.shp"
idField = "Unique_ID"
# ####################################### PROGRAMMING ######################################################### #
def BuildPolygon(lyr, LL, LR, UR, UL, id, whichPX):
# Build geometry, then write into new shapefile
	ring = ogr.Geometry(ogr.wkbLinearRing)
	ring.AddPoint(LL[0], LL[1])
	ring.AddPoint(UL[0], UL[1])
	ring.AddPoint(UR[0], UR[1])
	ring.AddPoint(LR[0], LR[1])
	ring.AddPoint(LL[0], LL[1])
	poly = ogr.Geometry(ogr.wkbPolygon)
	poly.AddGeometry(ring)
# Set ID field, set location
	featDef = outLYR.GetLayerDefn()
	featOut = ogr.Feature(featDef)
	featOut.SetGeometry(poly)
	featOut.SetField('ID', ID)
	featOut.SetField('wPX', whichPX)
# Create Feature, return lyr
	outLYR.CreateFeature(featOut)
pointsOpen = drvMemV.CopyDataSource(ogr.Open(points),'')
inLYR = pointsOpen.GetLayer()
# (1) Build output-shapefile
outSHP = drvV.CreateDataSource(outfile)
outLYR = outSHP.CreateLayer('outSHP', inLYR.GetSpatialRef(), geom_type=ogr.wkbPolygon)
IDfield = ogr.FieldDefn('ID', ogr.OFTInteger)
outLYR.CreateField(IDfield)
centerField = ogr.FieldDefn('wPX', ogr.OFTInteger)
outLYR.CreateField(centerField)
# (2) Loop through each feature in the point-shapefile and do the the operations
feat = inLYR.GetNextFeature()
while feat:
# Get the ID of the point, we need it for reference
	ID = feat.GetField(idField)
	print(ID)
# Get the geometry of the feature, get coordinates
	geom = feat.GetGeometryRef()
	mx, my = geom.GetX(), geom.GetY()
# Build the coordinates of the center polygon --> LL, LR, UR, UL
	BuildPolygon(outLYR, [mx-15, my-15], [mx+15, my-15], [mx+15, my+15], [mx-15, my+15], ID, 0)
# Upper left neighbor
	BuildPolygon(outLYR, [mx-45, my+15], [mx-15, my+15], [mx-15, my+45], [mx-45, my+45], ID, 1)
# Upper neighbor
	BuildPolygon(outLYR, [mx-15, my+15], [mx+15, my+15], [mx+15, my+45], [mx-15, my+45], ID, 2)
# Upper right neighbor
	BuildPolygon(outLYR, [mx+15, my+15], [mx+45, my+15], [mx+45, my+45], [mx+15, my+45], ID, 3)
# Right neighbor
	BuildPolygon(outLYR, [mx+15, my-15], [mx+45, my-15], [mx+45, my+15], [mx+15, my+15], ID, 4)
# Lower right neighbor
	BuildPolygon(outLYR, [mx+15, my-45], [mx+45, my-45], [mx+45, my-15], [mx+15, my-15], ID, 5)
# Lower neighbor
	BuildPolygon(outLYR, [mx-15, my-45], [mx+15, my-45], [mx+15, my-15], [mx-15, my-15], ID, 6)
# Lower left neighbor
	BuildPolygon(outLYR, [mx-45, my-45], [mx-15, my-45], [mx-15, my-15], [mx-45, my-15], ID, 7)
# Left neighbor
	BuildPolygon(outLYR, [mx-45, my-15], [mx-15, my-15], [mx-15, my+15], [mx-45, my+15], ID, 8)
# Switch to next feature, repeat
	feat = inLYR.GetNextFeature()




# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")