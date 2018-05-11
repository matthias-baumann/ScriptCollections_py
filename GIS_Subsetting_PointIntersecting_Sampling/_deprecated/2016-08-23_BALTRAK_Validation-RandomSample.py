# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import ogr, osr
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
classification = "B:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/baumann-etal_LandUseChange-Wilderness_Kostanay-KZ/Run09_ClumpSieve_10px_masked_clip.tif"
# ####################################### FUNCTIONS ########################################################### #
def StratifiedRandomSampleRaster(rasterFile, ListOfTupel, pointOut):
	# Create a single shp-file for each part of the tupel
	tempFileList = []
	for tupel in ListOfTupel:
		# Get tupel-info and generate filelists
		rasterclass = tupel[0]
		nr_points = tupel[1]
		outTMP = pointOut
		outTMP = outTMP.replace(".shp", "_TMP_class_" + str(rasterclass) + ".shp")
		tempFileList.append(outTMP)
		# Generate Random Array based on raster-value of interest
		ds = gdal.Open(rasterFile)
		gt = ds.GetGeoTransform()
		cols = ds.RasterXSize
		rows = ds.RasterYSize
		values = ds.GetRasterBand(1).ReadAsArray(0, 0, cols, rows)
		rn = np.random.random((rows, cols))
		mask = np.equal(values, rasterclass)
		choose = np.choose(mask, (0, rn))
		unique = np.unique(choose)
		select = unique[nr_points]
		mask = np.less_equal(choose, select)
		choose = np.choose(mask, (0, choose))
		# Write Point-shapefile for rastervalue
		(y_index, x_index) = np.nonzero(choose > 0)
		(upper_left_x, x_size, x_rotation, upper_left_y, y_rotation, y_size) = ds.GetGeoTransform()
		srs = osr.SpatialReference()
		srs.ImportFromWkt(ds.GetProjection())
		driver = ogr.GetDriverByName('ESRI Shapefile')
		shapeData = driver.CreateDataSource(outTMP)
		layer = shapeData.CreateLayer('ogr_pts', srs, ogr.wkbPoint)
		layerDefinition = layer.GetLayerDefn()
		fieldDefn = ogr.FieldDefn('Class', ogr.OFTInteger)
		layer.CreateField(fieldDefn)
		i = 0
		for x_coord in x_index:
			x = x_index[i] * x_size + upper_left_x + (x_size / 2) #add half the cell size
			y = y_index[i] * y_size + upper_left_y + (y_size / 2) #to centre the point
			point = ogr.Geometry(ogr.wkbPoint)
			point.SetPoint(0, x, y)
			feature = ogr.Feature(layerDefinition)
			feature.SetGeometry(point)
			feature.SetField('Class', rasterclass)
			layer.CreateFeature(feature)
			i = i + 1
		shapeData.Destroy()
	# Merge the temporary files into one single one
	for file in tempFileList:
		if not os.path.exists(pointOut):
			command = "ogr2ogr " + pointOut + " " + file
			os.system(command)
		else:
			command = "ogr2ogr -update -append " + pointOut + " " + file
			os.system(command)
	# Delete the tmp-point-Files
	deleteFolder = pointOut
	p = deleteFolder.rfind("/")
	deleteFolder = deleteFolder[:p+1]
	deleteList = os.listdir(deleteFolder)
	for file in deleteList:
		if file.find("_TMP_class_") >= 0:
			f = deleteFolder + file
			#os.remove(file)
	# Add and ID field to Shapefile
	driver = ogr.GetDriverByName('ESRI Shapefile')
	points = driver.Open(pointOut, 1)
	fieldDefn = ogr.FieldDefn('ID', ogr.OFTInteger)
	lyr = points.GetLayer()
	lyr.CreateField(fieldDefn)
	feature = lyr.GetNextFeature()
	id = 1
	while feature:
		feature.SetField('ID', id)
		lyr.SetFeature(feature)
		feature = lyr.GetNextFeature()
		id = id + 1
	lyr.ResetReading()
#(1) OLD GROW FOREST
pointOut = "B:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/baumann-etal_LandUseChange-Wilderness_Kostanay-KZ/01_Validation/StratifiedRandomSample_100ppc_Run09_20160823.shp"
StratifiedRandomSampleRaster(classification,
							 [[1,100],[2,100],[3,100],[4,100],[5,100],[6,100],[7,100],[8,100],[9,100],[10,100],[11,100],[12,100],[13,100],[14,100],[15,100]],
							 pointOut)

# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")