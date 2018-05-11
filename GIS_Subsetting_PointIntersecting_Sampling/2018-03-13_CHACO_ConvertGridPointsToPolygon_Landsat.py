# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import ogr
import baumiTools as bt
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " + starttime)
print("")
# ####################################### DRIVERS AND FOLDER-PATHS ############################################ #
drvV = ogr.GetDriverByName('ESRI Shapefile')
drvMemV = ogr.GetDriverByName('Memory')
points = "D:/baumamat/Warfare/_SHPs/BIOMES_TropicsSavannas_10kmGrid.shp"
outfile = "D:/baumamat/Warfare/_SHPs/BIOMES_TropicsSavannas_10kmGrid_polygons.shp"
# ####################################### PROGRAMMING ######################################################### #
# (1) LOAD THE SHAPEFILE INTO MEMORY, OPEN LAYER, CREATE SHAPEFILE IN MEMORY
# shpMem = bt.baumiVT.CopyToMem(points)
shpMem = ogr.Open(points)
lyrMem = shpMem.GetLayer()
pr = lyrMem.GetSpatialRef()
outSHP = drvMemV.CreateDataSource('')
outLYR = outSHP.CreateLayer('outSHP', pr, geom_type=ogr.wkbPolygon)
# (2) ADD FIELDS, RENAMED A LITTLE BIT
outSHP = bt.baumiVT.AddFieldToSHP(outSHP, "UniqueID", "int")
# (3) LOOP THROUGH POINT-FEATURES, CREATE POLYGON, AND ADD ATTRIBUTE VALUES
feat_p = lyrMem.GetNextFeature()
while feat_p:
# Get the field values --> this is set manually to make things easier
	pID = feat_p.GetField("UniqueID")
	print(pID)
# Calculate the polygon coordinates based on the point
	geom = feat_p.GetGeometryRef()
	mx, my = geom.GetX(), geom.GetY()
	LL = [mx - 5000, my - 5000]
	LR = [mx + 5000, my - 5000]
	UR = [mx + 5000, my + 5000]
	UL = [mx - 5000, my + 5000]
# Now build the new geometry
	square = ogr.Geometry(ogr.wkbLinearRing)
	square.AddPoint(LL[0], LL[1])
	square.AddPoint(UL[0], UL[1])
	square.AddPoint(UR[0], UR[1])
	square.AddPoint(LR[0], LR[1])
	square.AddPoint(LL[0], LL[1])
	poly = ogr.Geometry(ogr.wkbPolygon)
	poly.AddGeometry(square)
# Create the feature, set the values
	featDef = outLYR.GetLayerDefn()
	featOut = ogr.Feature(featDef)
	featOut.SetGeometry(poly)
	featOut.SetField('UniqueID', pID)
# Create the feature, get the next feature
	outLYR.CreateFeature(featOut)
	feat_p = lyrMem.GetNextFeature()
# Copy the file to disk
bt.baumiVT.CopySHPDisk(outSHP, outfile)

# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")
