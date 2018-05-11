# ######################################## LOAD REQUIRED MODULES ############################################## #
import os
import time
import datetime
import ogr
import osr
import gdal
import numpy as np
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:", starttime)
print("")
# ####################################### BUILD GLOBAL FUNCTIONS ############################################## #

def RandomPoints_Raster(rasterFile, points, rastervalues, output):
	print("Input-raster: " + rasterFile)
	print("Sample from classes: " + str(rastervalues)[1:-1])
	print("Points per class: " + str(points))
	print("Output-shpFile: " + output)
	
	def RandomPoints_Rastersubclass(rasterFile, points, value, outTMP):
		# Generate Random Array based on rastervalue of interest
		ds = gdal.Open(rasterFile)
		gt = ds.GetGeoTransform()
		cols = ds.RasterXSize
		rows = ds.RasterYSize
		values = ds.GetRasterBand(1).ReadAsArray(0, 0, cols, rows)
		rn = np.random.random((rows, cols))
		mask = np.equal(values, value)
		choose = np.choose(mask, (0, rn))
		unique = np.unique(choose)
		select = unique[no_points]
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
		fieldDefn = ogr.FieldDefn('Class_ID', ogr.OFTInteger)
		layer.CreateField(fieldDefn)
		fieldDefn = ogr.FieldDefn('Class', ogr.OFTInteger)
		layer.CreateField(fieldDefn)		
		i = 0
		id = 1
		for x_coord in x_index:
			x = x_index[i] * x_size + upper_left_x + (x_size / 2) #add half the cell size
			y = y_index[i] * y_size + upper_left_y + (y_size / 2) #to centre the point
			
			point = ogr.Geometry(ogr.wkbPoint)
			point.SetPoint(0, x, y)
			feature = ogr.Feature(layerDefinition)
			feature.SetGeometry(point)
			feature.SetField('Class_ID', id)
			feature.SetField('Class', value)
			layer.CreateFeature(feature)
			i = i + 1
			id = id + 1
		shapeData.Destroy()
	
	def MergeTempShapefiles_DeleteTemp(tempFileList, output):
		for file in tempFileList:
			if not os.path.exists(output):
				command = "ogr2ogr " + output + " " + file
				os.system(command)
			else:
				command = "ogr2ogr -update -append " + output + " " + file
				os.system(command)
			
		# delete the TMP-Point-Files
		deleteFolder = output
		p = deleteFolder.rfind("/")
		deleteFolder = deleteFolder[:p+1]
		deleteList = os.listdir(deleteFolder)
		for file in deleteList:
			if file.find("_TMP_class_") >= 0:
				f = deleteFolder + file
				os.remove(f)
	
	def AddIDfieldToSHP(output):
		driver = ogr.GetDriverByName('ESRI Shapefile')
		points = driver.Open(output, 1)
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
	
	tempFileList = []
	for value in rastervalues:
		outTMP = output
		outTMP = outTMP.replace(".shp", "_TMP_class_" + str(value) + ".shp")
		tempFileList.append(outTMP)
		RandomPoints_Rastersubclass(rasterFile, points, value, outTMP)
	MergeTempShapefiles_DeleteTemp(tempFileList, output)
	AddIDfieldToSHP(output)
	
# ####################################### RUN THE MODULES AND CALL THE FUNCTIONS ############################## #
# (1)  GENERATE RANDOM POINTS WITHIN RASTER FOR CLASS VALUES 'RASTERVALUES'
rasterFile = "D:/Matthias/Projects-and-Publications/Publications/Publications-in-review/2013_Butsic-etal_Congo_LandCoverChange-and-War/Process01_Generate-new-1990map/02_ForestChange_FootprintsOutline_Intersect.tif"
no_points = 200
rastervalues = [1, 2, 3, 4, 5]
outSHP = "D:/Matthias/Projects-and-Publications/Publications/Publications-in-review/2013_Butsic-etal_Congo_LandCoverChange-and-War/Process01_Generate-new-1990map/02_RandomSample_200PointsPerClass.shp"
RandomPoints_Raster(rasterFile, no_points, rastervalues, outSHP)

# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #		
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: ", starttime)
print("end: ", endtime)
print("")