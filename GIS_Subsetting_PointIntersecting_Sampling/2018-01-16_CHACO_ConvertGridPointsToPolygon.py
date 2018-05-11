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
points = "L:/_SHARED_DATA/CL_MB/tc_sc/_Version02_300m/points_300m_clip_withValues.shp"
outfile = "L:/_SHARED_DATA/CL_MB/tc_sc/_Version02_300m/polygons_300m_clip_withValues.shp"
# ####################################### PROGRAMMING ######################################################### #
# (1) LOAD THE SHAPEFILE INTO MEMORY, OPEN LAYER, CREATE SHAPEFILE IN MEMORY
# shpMem = bt.baumiVT.CopyToMem(points)
shpMem = ogr.Open(points)
lyrMem = shpMem.GetLayer()
pr = lyrMem.GetSpatialRef()
outSHP = drvMemV.CreateDataSource('')
outLYR = outSHP.CreateLayer('outSHP', pr, geom_type=ogr.wkbPolygon)
# (2) ADD FIELDS, RENAMED A LITTLE BIT
outSHP = bt.baumiVT.AddFieldToSHP(outSHP, "PointID", "int")
outSHP = bt.baumiVT.AddFieldToSHP(outSHP, "TC_LS", "int")
outSHP = bt.baumiVT.AddFieldToSHP(outSHP, "SC_LS", "int")
outSHP = bt.baumiVT.AddFieldToSHP(outSHP, "TC_L", "int")
outSHP = bt.baumiVT.AddFieldToSHP(outSHP, "SC_L", "int")
outSHP = bt.baumiVT.AddFieldToSHP(outSHP, "TC_S", "int")
outSHP = bt.baumiVT.AddFieldToSHP(outSHP, "SC_S", "int")
# (3) LOOP THROUGH POINT-FEATURES, CREATE POLYGON, AND ADD ATTRIBUTE VALUES
feat_p = lyrMem.GetNextFeature()
while feat_p:
# Get the field values --> this is set manually to make things easier
	pID = feat_p.GetField("pointid")
	print(pID)
	TC_LS = int(float(feat_p.GetField("points_300")))
	SC_LS = int(float(feat_p.GetField("points_3_1")))
	TC_L = int(float(feat_p.GetField("points_3_2")))
	SC_L = int(float(feat_p.GetField("points_3_3")))
	TC_S = int(float(feat_p.GetField("points_3_4")))
	SC_S = int(float(feat_p.GetField("points_3_5")))
# Calculate the polygon coordinates based on the point
	geom = feat_p.GetGeometryRef()
	mx, my = geom.GetX(), geom.GetY()
	LL = [mx - 150, my - 150]
	LR = [mx + 150, my - 150]
	UR = [mx + 150, my + 150]
	UL = [mx - 150, my + 150]
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
	featOut.SetField('PointID', pID)
	featOut.SetField('TC_LS', TC_LS)
	featOut.SetField('SC_LS', SC_LS)
	featOut.SetField('TC_L', TC_L)
	featOut.SetField('SC_L', SC_L)
	featOut.SetField('TC_S', TC_S)
	featOut.SetField('SC_S', SC_S)
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
