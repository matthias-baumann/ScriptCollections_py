# ######################################## REQUIRED MODULES ################################################### #
import os, sys
import time, datetime
import ogr, osr
import gdal
from gdalconst import *
import numpy as np
import scipy
import scipy.ndimage
import csv
import itertools
import struct
# ####################################### GIS TOOLS ########################################################### #
# (1) RASTER PROCESSING TOOLS
# Simply clips the extent of a raster to the extent of a polygon-file
# Files have to be in the same coordinate-system
def SetRasterExtentByPolygon(polygon_Input, raster_Input, raster_Output, type_Output): # "GTiff"=tif, "HFA"=img, "ENVI"=bsq
	print("Executing: SetRasterExtentByPolygon")
	# Get pixel size from raster
	in_ds = gdal.Open(raster_Input)
	gt = in_ds.GetGeoTransform()
	pixelsize = gt[1]
	# Convert polygon to raster
	input = polygon_Input
	out_TMP = input
	out_TMP = out_TMP.replace(".shp", ".tif")
	#command = "gdal_rasterize -burn 1 -tr " + str(pixelsize) + " " + str(pixelsize) + " -ot Int16 -q -of GTiff " + input + " " + out_TMP
	command = "gdal_rasterize -burn 1 -tr " + str(pixelsize) + " " + str(pixelsize) + " -q -of GTiff " + input + " " + out_TMP
	os.system(command)
	# Clip Raster based on extent of temporary raster
	ds = gdal.Open(out_TMP)
	gt = ds.GetGeoTransform()
	cols = ds.RasterXSize
	rows = ds.RasterYSize
	ext = []
	xarr = [0,cols]
	yarr = [0,rows]
	for px in xarr:
		for py in yarr:
			x = gt[0] + (px*gt[1])+(py*gt[2])
			y = gt[3] + (px*gt[4])+(py*gt[5])
			ext.append([x,y])
		yarr.reverse()
	#command = "gdal_translate -q -ot Byte -of " + type_Output + " -projwin " + str((ext[0][0])) + " " + str((ext[0][1])) + " " + str((ext[2][0])) + " " + str((ext[2][1])) + " " + raster_Input + " " + raster_Output
	command = "gdal_translate -q -of " + type_Output + " -projwin " + str((ext[0][0])) + " " + str((ext[0][1])) + " " + str((ext[2][0])) + " " + str((ext[2][1])) + " " + raster_Input + " " + raster_Output
	os.system(command)
	ds = None
	# Remove temp-File
	p = out_TMP.rfind("/")
	folder = out_TMP[:p+1]
	list = os.listdir(folder)
	os.remove(out_TMP)
# Clips raster file and masks new raster by value of a field in a polygon layer
def MaskRasterByPolygon(polygon_Input, polygon_field, raster_Input, raster_Output, type_Output): # "GTiff"=tif, "HFA"=img, "ENVI"=bsq
	print("Executing: MaskRasterByPolygon")
	# Make check if all entries of polygon_field[polygon_file] are greater than zero
	checkList = []
	polygon = ogr.Open(polygon_Input)
	lyr = polygon.GetLayer()
	feature = lyr.GetNextFeature()
	while feature:
		value = feature.GetField(polygon_field)
		checkList.append(int(value))
		feature = lyr.GetNextFeature()
	lyr.ResetReading()
	polygon = None
	if 0 in checkList:
		print("Some entries in the Polygon-File contain the value '0'")
		print("Choose field with all Values > 0 and run script again")
	else:
		# Get pixel size from raster
		in_ds = gdal.Open(raster_Input)
		gt = in_ds.GetGeoTransform()
		pixelsize = gt[1]
		# Convert polygon to raster
		input = polygon_Input
		out_TMP = input
		out_TMP = out_TMP.replace(".shp", "TMPFile.tif")
		# create Layer-Name
		(shpPath, shpName) = os.path.split(input)
		(shapeShort, shapeExt) = os.path.splitext(shpName)
		#command = "gdal_rasterize -l " + shapeShort + " -a " + polygon_field + " -tr " + str(pixelsize) + " " + str(pixelsize) + " -ot Int16 -q -of GTiff " + input + " " + out_TMP
		command = "gdal_rasterize -l " + shapeShort + " -a " + polygon_field + " -tr " + str(pixelsize) + " " + str(pixelsize) + " -q -of GTiff " + input + " " + out_TMP
		os.system(command)
		# Clip Raster based on extent of temporary raster
		out_TMP02 = out_TMP
		out_TMP02 = out_TMP02.replace(".tif","02.img")
		ds = gdal.Open(out_TMP)
		gt = ds.GetGeoTransform()
		cols = ds.RasterXSize
		rows = ds.RasterYSize
		ext = []
		xarr = [0,cols]
		yarr = [0,rows]
		for px in xarr:
			for py in yarr:
				x = gt[0] + (px*gt[1])+(py*gt[2])
				y = gt[3] + (px*gt[4])+(py*gt[5])
				ext.append([x,y])
			yarr.reverse()
		#command = "gdal_translate -q -ot Byte -of " + type_Output + " -projwin " + str((ext[0][0])) + " " + str((ext[0][1])) + " " + str((ext[2][0])) + " " + str((ext[2][1])) + " " + raster_Input + " " + out_TMP02
		command = "gdal_translate -q -of " + type_Output + " -projwin " + str((ext[0][0])) + " " + str((ext[0][1])) + " " + str((ext[2][0])) + " " + str((ext[2][1])) + " " + raster_Input + " " + out_TMP02
		os.system(command)
		ds = None
		# Do the masking
		# (a) Get all information from the input-files
		out_TMP_gdal = gdal.Open(out_TMP)
		out_TMP02_gdal = gdal.Open(out_TMP02)
		cols = out_TMP_gdal.RasterXSize
		rows = out_TMP_gdal.RasterYSize
		rb_TMP = out_TMP_gdal.GetRasterBand(1)
		rb_TMP02 = out_TMP02_gdal.GetRasterBand(1)		
		out_dataType = rb_TMP02.DataType
		# (b) build the output-file with the properties	
		outDrv = gdal.GetDriverByName(type_Output)
		out = outDrv.Create(raster_Output, cols, rows, 1, out_dataType)
		out.SetProjection(out_TMP02_gdal.GetProjection())
		out.SetGeoTransform(out_TMP02_gdal.GetGeoTransform())
		rb_out = out.GetRasterBand(1)
		rb_out.SetCategoryNames(rb_TMP02.GetCategoryNames())
		rb_out.SetColorTable(rb_TMP02.GetColorTable())
		rb_out.SetNoDataValue(0)
		# (c) Process the raster		
		for y in range(rows):
			tmp01 = rb_TMP.ReadAsArray(0,y,cols,1)
			tmp02 = rb_TMP02.ReadAsArray(0,y,cols,1)
			dataOut = tmp02
			np.putmask(dataOut, tmp01 == 0, 0)
			# dataOut.shape = (1,-1)
			rb_out.WriteArray(dataOut, 0,y)
		out_TMP_gdal = None
		out_TMP02_gdal = None
		rb_out.SetDefaultRAT()
		rb_out = None
		# Remove temp-File
		p = out_TMP.rfind("/")
		folder = out_TMP[:p+1]
		list = os.listdir(folder)
		os.remove(out_TMP)
		os.remove(out_TMP02)
		extraTMP02 = out_TMP02 + ".aux.xml"
		os.remove(extraTMP02)
# Re-Classify a raster based on tupel values, e.g., tupel = [[0,0],[1,1],[2,2],[1,3],[1,4]]
def ReclassifyRaster(inputRaster, tupelList, outputRaster, type_Output): # "GTiff"=tif, "HFA"=img, "ENVI"=bsq
	# Open the input-file
	ds = gdal.Open(inputRaster, GA_ReadOnly)
	cols = ds.RasterXSize
	rows = ds.RasterYSize
	raster = ds.GetRasterBand(1)
	out_dataType = raster.DataType
	# Create and format the output-file
	outDrv = gdal.GetDriverByName(type_Output)
	out = outDrv.Create(outputRaster, cols, rows, 1, out_dataType)
	out.SetProjection(ds.GetProjection())
	out.SetGeoTransform(ds.GetGeoTransform())
	out_ras = out.GetRasterBand(1)
	out_ras.SetCategoryNames(raster.GetCategoryNames())
	out_ras.SetColorTable(raster.GetColorTable())
	# Process the raster
	for y in range(rows):
		tmp = raster.ReadAsArray(0,y,cols,1)
		dataOut = tmp
		for combo in tupelList:
			in_val = combo[0]
			out_val = combo[1]
			np.putmask(dataOut, tmp == in_val, out_val)
		out_ras.WriteArray(dataOut, 0, y)
	ds = None
# Converts MODIS-subdataset into GTiff-file, projection remains the same (sinosodial)
# Get subdataset-name via "gdalinfo" before running this function, filenames have to be entire pathnames
# ndvi --> '":MODIS_Grid_16DAY_250m_500m_VI:250m 16 days NDVI"'
# doy --> '":MODIS_Grid_16DAY_250m_500m_VI:250m 16 days composite day of the year"'
def ConvertMODIS_hdfToTiff(inputHDF, outputTIF, subDataset):
	p = inputHDF.rfind("/")
	file = inputHDF[p+1:len(inputHDF)]
	command = 'gdal_translate -q -of GTiff "HDF4_EOS:EOS_GRID:"' + inputHDF + subDataset + " " + outputTIF
	os.system(command)
# calculate anomalies from the mean for multi-band image (for each band)
def CalculateAnomalies(input_path, output_path):
	print("Calculating Anomalies for: ", input_path)
	ds = gdal.Open(input_path, GA_ReadOnly)
	# Get all the info that is stored in the file
	cols = ds.RasterXSize
	rows = ds.RasterYSize
	bandNR = ds.RasterCount
	# Create the output-file
	outDrv = gdal.GetDriverByName('GTiff')
	outfile = outDrv.Create(output_path, cols, rows, bandNR, GDT_Float32)
	outfile.SetProjection(ds.GetProjection())
	outfile.SetGeoTransform(ds.GetGeoTransform())
	# Now do the operation
	for row in range(rows):
		# (1) Create the mean values
		goatse = np.zeros(shape=(bandNR,cols))
		for band in range(bandNR):
			b = band + 1
			vals = ds.GetRasterBand(b).ReadAsArray(0,row,cols,1)
			goatse[band] = vals
		#print(goatse)
		# Build the mean of bands
		mean_goatse = np.mean(goatse, axis=0)
		#print(mean_goatse)
		# Subtract the value of the band from the mean
		goatse_diff = np.subtract(goatse, mean_goatse)
		#print(goatse_diff)
		for band in range(bandNR):
			b = band + 1
			dataOut = goatse_diff[band]
			dataOut = np.expand_dims(dataOut, axis=0)
			outfile.GetRasterBand(b).WriteArray(dataOut, 0, row)
	ds = None
	
	
	
	
# ##########################################	
# (2) VECTOR PROCESSING TOOLS
# Clips shapefile by another shapefile. Outfile will be in coordinates of clip-file
def ClipShapefileByShapefile(polygon_Input, polygon_Clip, polygon_Output):
	print("Executing: ClipShapefileByShapefile")
	# (1) reproject clip-polygon to coordniate-system of input-polygon
	# Get the layers coordinate-systems	
	input = ogr.Open(polygon_Input)
	input_lyr = input.GetLayer()
	input_srs = input_lyr.GetSpatialRef()
	wkt = input_srs.ExportToWkt()
	input_lyr = None
	input = None
	# Build the temporary shape-file where we reproject the clip-polygon to
	outTMP = polygon_Clip
	outTMP = outTMP.replace(".shp", "TMPproject_01.shp")
	command = "ogr2ogr -t_srs " + wkt + " " + outTMP + " " + polygon_Clip
	os.system(command)
	# (2) Clip the input_layer by extent of projected clip-layer
	outTMP02 = outTMP
	outTMP02 = outTMP.replace("1.shp","2.shp")
	command = "ogr2ogr -clipsrc " + outTMP + " " + outTMP02 + " " + polygon_Input
	os.system(command)
	# (3) Convert the clipped layer back into the initial coordinate system
	clip = ogr.Open(polygon_Clip)
	clip_lyr = clip.GetLayer()
	clip_srs = clip_lyr.GetSpatialRef()
	wkt = clip_srs.ExportToWkt()
	clip_lyr = None
	clip = None
	command = "ogr2ogr -t_srs " + wkt + " " + polygon_Output + " " + outTMP02
	os.system(command)
	# (4) Remove the TMP-file
	p = outTMP.rfind("/")
	folder = outTMP[:p+1]
	list = os.listdir(folder)
	for file in list[:]:
		if file.find("TMPproject") >= 0:
			remove = folder + file
			os.remove(remove)			
# Merge list of shapefiles, file-paths have to be complete
def MergeSHPfiles(listOfSHPfiles, shpOut):
	# Merge the temporary files into one single one
	for file in listOfSHPfiles:
		if not os.path.exists(shpOut):
			command = "ogr2ogr " + shpOut + " " + file
			os.system(command)
		else:
			command = "ogr2ogr -update -append " + shpOut + " " + file
			os.system(command)
# Add and calculate a field to a shapefile
def AddIDField(shp):
	driver = ogr.GetDriverByName('ESRI Shapefile')
	points = driver.Open(shp, 1)
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
# Convert any vector-type input-shapefile to raster-output, ha to be .tif
def ConvertVectorToRaster(vectorInput,rasterOutput,idField,resolution_m):
	# needed modules
	import gdal, osr, ogr
	output = vectorInput
	output = output.replace("shp","_asRaster.tif")
	command = "gdal_rasterize -a " + idField + " -tr " + str(resolution_m) + " " + str(resolution_m) + " -q " + vectorInput + " " + output
	os.system(command)

# #########################################			
# (3) MISCELLANOUS
# Simple random sample based on raster-extent
def SimpleRandomSampleRaster(rasterFile, no_points, pointOut):
	# Generate Random Array based on raster-value of interest
	ds = gdal.Open(rasterFile)
	gt = ds.GetGeoTransform()
	cols = ds.RasterXSize
	rows = ds.RasterYSize
	values = ds.GetRasterBand(1).ReadAsArray(0, 0, cols, rows)
	rn = np.random.random((rows, cols))
	unique = np.unique(rn)
	select = unique[no_points]
	mask = np.less_equal(rn, select)
	choose = np.choose(mask, (0, rn))
	# Write Point-shapefile for rastervalue
	(y_index, x_index) = np.nonzero(choose > 0)
	(upper_left_x, x_size, x_rotation, upper_left_y, y_rotation, y_size) = ds.GetGeoTransform()
	srs = osr.SpatialReference()
	srs.ImportFromWkt(ds.GetProjection())
	driver = ogr.GetDriverByName('ESRI Shapefile')
	shapeData = driver.CreateDataSource(pointOut)
	layer = shapeData.CreateLayer('ogr_pts', srs, ogr.wkbPoint)
	layerDefinition = layer.GetLayerDefn()
	fieldDefn = ogr.FieldDefn('ID', ogr.OFTInteger)
	layer.CreateField(fieldDefn)
	i = 0
	for x_coord in x_index:
		x = x_index[i] * x_size + upper_left_x + (x_size / 2) #add half the cell size
		y = y_index[i] * y_size + upper_left_y + (y_size / 2) #to centre the point
		point = ogr.Geometry(ogr.wkbPoint)
		point.SetPoint(0, x, y)
		feature = ogr.Feature(layerDefinition)
		feature.SetGeometry(point)
		id = i + 1
		feature.SetField('ID', id)
		layer.CreateFeature(feature)
		i = i + 1
	shapeData.Destroy()
# Generate random points in ClassificationFile, define classes/nr_points in tupel, e.g. tupel = [[1,50],[2,50],[3,50],[4,50]]
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
			os.remove(file)
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
# Generate random points in Polygon-File, define field in polygon for stratification and number of points per strata
def StratifiedRandomSamplePolygon(polygonFile, classField, pointsperclass, pointOutput):
	# Convert the polygon-File to a raster
	rasterTMP = polygonFile
	rasterTMP = rasterTMP.replace(".shp","_TMPraster.tif")
	(shpPath, shpName) = os.path.split(polygonFile)
	(shapeShort, shapeExt) = os.path.splitext(shpName)
	command = "gdal_rasterize -l " + shapeShort + " -a " + classField + " -tr 30 30 -q -of GTiff " + polygonFile + " " + rasterTMP
	os.system(command)
	# Open newly generated TIFF file and extract all information needed
	ds = gdal.Open(rasterTMP)
	gt = ds.GetGeoTransform()
	cols = ds.RasterXSize
	rows = ds.RasterYSize
	array = ds.GetRasterBand(1).ReadAsArray(0, 0, cols, rows)
	raster_unique = np.unique(array)
	raster_unique = raster_unique[raster_unique > 0]
	# Loop through each class in raster_unique and generate a random sample of points based on number given in input
	tempfileList = []
	for value in raster_unique:
		pointTMP = pointOutput
		pointTMP = pointTMP.replace(".shp", "_TMP_class_" + str(value) + ".shp")
		tempfileList.append(pointTMP)
		# Generate random array
		rn = np.random.random((rows, cols))
		mask = np.equal(array, value)
		choose = np.choose(mask, (0, rn))
		unique = np.unique(choose)
		select = unique[pointsperclass]
		mask = np.less_equal(choose, select)
		choose = np.choose(mask, (0, choose))
		# Write point-shapefile for rastervalue
		(y_index, x_index) = np.nonzero(choose > 0)
		(upper_left_x, x_size, x_rotation, upper_left_y, y_rotation, y_size) = ds.GetGeoTransform()
		srs = osr.SpatialReference()
		srs.ImportFromWkt(ds.GetProjection())
		driver = ogr.GetDriverByName('ESRI Shapefile')
		shapeData = driver.CreateDataSource(pointTMP)
		layer = shapeData.CreateLayer('ogr_pts', srs, ogr.wkbPoint)
		layerDefinition = layer.GetLayerDefn()
		fieldDefn = ogr.FieldDefn(classField, ogr.OFTInteger)
		layer.CreateField(fieldDefn)
		i = 0
		for x_coord in x_index:
			x = x_index[i] * x_size + upper_left_x + (x_size / 2) #add half the cell size
			y = y_index[i] * y_size + upper_left_y + (y_size / 2) #to centre the point
			point = ogr.Geometry(ogr.wkbPoint)
			point.SetPoint(0, x, y)
			feature = ogr.Feature(layerDefinition)
			feature.SetGeometry(point)
			feature.SetField(classField, value)
			layer.CreateFeature(feature)
			i = i + 1
		shapeData.Destroy()
	array = None
	ds = None	# Merge the temporary files into one single one
	for file in tempfileList:
		if not os.path.exists(pointOutput):
			command = "ogr2ogr " + pointOutput + " " + file
			os.system(command)
		else:
			command = "ogr2ogr -update -append " + pointOutput + " " + file
			os.system(command)
	# Delete the tmp-point-Files
	deleteFolder = pointOutput
	p = deleteFolder.rfind("/")
	deleteFolder = deleteFolder[:p+1]
	deleteList = os.listdir(deleteFolder)
	for file in deleteList:
		if file.find("_TMP") >= 0:
			f = deleteFolder + file
			os.remove(file)	
	# Add and ID field to Shapefile
	driver = ogr.GetDriverByName('ESRI Shapefile')
	points = driver.Open(pointOutput, 1)
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
# Generate a zonal histogram of a polygon-file on top of a classification file	
def ZonalHistogram(polygonFile, rasterFile, idField, outputTable):
	print("Performing Zonal Histogram")
	# Get extent and Pixel-size from raster
	ds = gdal.Open(rasterFile)
	gt = ds.GetGeoTransform()
	cols = ds.RasterXSize
	rows = ds.RasterYSize
	ext = []
	xarr = [0,cols]
	yarr = [0,rows]
	for px in xarr:
		for py in yarr:
			x = gt[0] + (px*gt[1])+(py*gt[2])
			y = gt[3] + (px*gt[4])+(py*gt[5])
			ext.append([x,y])
		yarr.reverse()
	PixelSize = gt[1]
	pr = ds.GetProjection()
	ds = None
	# Re-Project polygon-file
	polyTMP = polygonFile
	polyTMP = polyTMP.replace(".shp","_TMPconvert.shp")
	command = "ogr2ogr -t_srs " + pr + " " + polyTMP + " " + polygonFile
	os.system(command)
	# Convert the Polygon-File to raster
	outTMP = polyTMP
	outTMP = outTMP.replace(".shp", "_asRaster.tif")
	#command = "gdal_rasterize -a " + idField + " -tr " + str(PixelSize) + " " + str(PixelSize) + " -ot Int16 -q -of GTiff -te " + str((ext[1][0])) + " " + str((ext[1][1])) + " " + str((ext[2][0])) + " " + str((ext[0][1])) + " " + polyTMP + " " + outTMP
	command = "gdal_rasterize -a " + idField + " -tr " + str(PixelSize) + " " + str(PixelSize) + " -q -of GTiff -te " + str((ext[1][0])) + " " + str((ext[1][1])) + " " + str((ext[2][0])) + " " + str((ext[0][1])) + " " + polyTMP + " " + outTMP
	os.system(command)
	# Zonal histogram
	# Load properties and bands
	outTMP_gdal = gdal.Open(outTMP, GA_ReadOnly)
	raster_gdal = gdal.Open(rasterFile, GA_ReadOnly)
	cols = outTMP_gdal.RasterXSize
	rows = outTMP_gdal.RasterYSize
	pols = outTMP_gdal.GetRasterBand(1)
	vals = raster_gdal.GetRasterBand(1)
	np.seterr(all='ignore')
	vals_array = vals.ReadAsArray(0, 0, cols, rows)
	pols_array = pols.ReadAsArray(0, 0, cols, rows)
	# Get the unqiue values from the classification file, create output-list for it
	raster_unique = np.unique(vals_array)
	raster_unique = raster_unique[raster_unique >= 0]
	list = raster_unique.tolist()
	ras_IDs_unique = ["EMPTY"]
	for l in list:
		ras_IDs_unique.append(l)
	# Temporarily convert the raster into continuous values
	i = 0
	for l in list:
		np.putmask(vals_array, vals_array == l, i)
		i = i + 1
	ras_unique02 = np.unique(vals_array)
	ras_unique02 = ras_unique02[ras_unique02 >= 0]
	# Get the unique values from the polygon file
	index = np.unique(pols_array)
	index = np.delete(index, 0, axis=0)
	polyIDs_unique = index.tolist()
	statement = "global histo; histo = np.ndarray.tolist(scipy.ndimage.measurements.histogram(vals_array, bins = len(ras_unique02), min = np.min(ras_unique02), max = np.max(ras_unique02), labels = pols_array, index = index))"
	exec(statement)	
	summary = np.array(histo).tolist()
	pols_array = None
	pols = None
	vals = None
	polygons_gdal = None
	values_gdal = None
	# Create the lists for the output
	values = []
	values.append(ras_IDs_unique)
	for polID in polyIDs_unique:
		i = polyIDs_unique.index(polID)
		rowvals = []
		rowvals.append(polID)
		val = summary[i]
		for v in val:
			rowvals.append(v)
		values.append(rowvals)
	# write output into csv-file
	with open(outputTable, "w") as the_file:
		csv.register_dialect("custom", delimiter=",",skipinitialspace=True, lineterminator='\n')
		writer = csv.writer(the_file, dialect="custom")
		for element in values:
			writer.writerow(element)
	# Delete temporary raster
	p = polygonFile.rfind("/")
	deleteFolder = polygonFile[:p+1]
	deleteList = os.listdir(deleteFolder)
	for file in deleteList:
		if file.find("_TMPconvert") >= 0:
			delete = deleteFolder + file
			os.remove(delete)
# Calculate zonal statistics of polygon-file overlaid over a raster
# --> add to zonal stats the homogenization of the coordinate system of the polygon file
def ZonalStatistics(polygonFile, id_field, rasterFile, variableName, output_csv):
	# Needed modules
	import gdal, osr, org, scipy, scipy.ndimage, numpy as np, os, csv, itertools
	# (1) Get the unique values of the polygon-file we do the zonalstats for
	IDs = []
	IDs.append(id_field)
	polygons = ogr.Open(polygonFile)
	lyr = polygons.GetLayer()
	feature = lyr.GetNextFeature()
	while feature:
		id = feature.GetField(id_field)
		IDs.append(id)
		feature = lyr.GetNextFeature()
	lyr.ResetReading()
	# (2) Get Extent and pixelsize from raster-file, convert polygonFile to raster
	ds = gdal.Open(rasterFile)
	gt = ds.GetGeoTransform()
	ps = gt[1]
	cols = ds.RasterXSize
	rows = ds.RasterYSize
	ext = []
	xarr = [0,cols]
	yarr = [0,rows]
	for px in xarr:
		for py in yarr:
			x = gt[0] + (px*gt[1])+(py*gt[2])
			y = gt[3] + (px*gt[4])+(py*gt[5])
			ext.append([x,y])
		yarr.reverse()
	pr = ds.GetProjection()
	ds = None
	# Re-Project polygon-file
	polyTMP = polygonFile
	polyTMP = polyTMP.replace(".shp","_TMPconvert.shp")
	command = "ogr2ogr -t_srs " + pr + " " + polyTMP + " " + polygonFile
	os.system(command)
	# Convert the Polygon-File to raster
	outTMP = polyTMP
	outTMP = outTMP.replace(".shp", "_asRaster.tif")
	outTMP = polygonFile
	outTMP = outTMP.replace(".shp", "_asRasterTMP.tif")
	#command = "gdal_rasterize -a " + id_field + " -tr " + str(ps) + " " + str(ps) + " -ot UInt16 -q -of GTiff -te " + str((ext[1][0])) + " " + str((ext[1][1])) + " " + str((ext[2][0])) + " " + str((ext[0][1])) + " " + polyTMP + " " + outTMP
	command = "gdal_rasterize -a " + id_field + " -tr " + str(ps) + " " + str(ps) + " -q -of GTiff -te " + str((ext[1][0])) + " " + str((ext[1][1])) + " " + str((ext[2][0])) + " " + str((ext[0][1])) + " " + polyTMP + " " + outTMP
	os.system(command)
	# (3) Do the zonal statistics
	mean = []
	meanVar = variableName + "_mean"
	mean.append(meanVar)
	sd = []
	sdVar = variableName + "_sd"
	sd.append(sdVar)
	max = []
	maxVar = variableName + "_max"
	max.append(maxVar)
	min = []
	minVar = variableName + "_min"
	min.append(minVar)
	sum = []
	sumVar = variableName + "_sum"
	sum.append(sumVar)
	pols_gdal = gdal.Open(outTMP, GA_ReadOnly)
	ras_gdal = gdal.Open(rasterFile, GA_ReadOnly)
	cols = pols_gdal.RasterXSize
	rows = pols_gdal.RasterYSize
	pol = pols_gdal.GetRasterBand(1).ReadAsArray(0, 0, cols, rows)
	ras = ras_gdal.GetRasterBand(1).ReadAsArray(0, 0, cols, rows)
	np.seterr(all='ignore')
	index = np.unique(pol)
	index = np.delete(index, 0, axis=0)# Remove the zero item, which is background in the raster
	statement = "global stat,vals; vals = np.ndarray.tolist(scipy.ndimage.measurements.mean(ras, labels = pol, index = index))"
	exec(statement)
	mean = mean + vals
	statement = "global stat,vals; vals = np.ndarray.tolist(scipy.ndimage.measurements.standard_deviation(ras, labels = pol, index = index))"
	exec(statement)
	sd = sd + vals
	statement = "global stat,vals; vals = np.ndarray.tolist(scipy.ndimage.measurements.maximum(ras, labels = pol, index = index))"
	exec(statement)
	max = max + vals
	statement = "global stat,vals; vals = np.ndarray.tolist(scipy.ndimage.measurements.minimum(ras, labels = pol, index = index))"
	exec(statement)
	min = min + vals
	statement = "global stat,vals; vals = np.ndarray.tolist(scipy.ndimage.measurements.sum(ras, labels = pol, index = index))"
	exec(statement)
	sum = sum + vals
	pols_gdal = None
	ras_gdal = None
	# (4) Write the output-file
	outlist = zip(IDs, mean, sd, max, min, sum)
	with open(output_csv, "w") as the_file:
		csv.register_dialect("custom", delimiter=",", skipinitialspace=True, lineterminator='\n')
		writer = csv.writer(the_file, dialect="custom")
		for element in outlist:
			writer.writerow(element)
	# (5) Delete the temporary raster
	p = polygonFile.rfind("/")
	deleteFolder = polygonFile[:p+1]
	deleteList = os.listdir(deleteFolder)
	for file in deleteList:
		if file.find("_TMPconvert") >= 0:
			try:
				delete = deleteFolder + file
				os.remove(delete)
			except:
				print("Could not delete temporary file, remove manually. Files are in folder:")
				print(deleteFolder)
# Calculate the distance pixels of value 'RasterValue'
def CalculateDistanceToRaster(inputRaster, RasterValue, outputRaster):
	print("Calculating Distance to Raster-value")
	# (1) Re-class the raster, so that all values other than forest have one value
	# Load the input-raster
	ds = gdal.Open(inputRaster, GA_ReadOnly)
	gt = ds.GetGeoTransform()
	cols = ds.RasterXSize
	rows = ds.RasterYSize
	rb = ds.GetRasterBand(1)
	# Create the output-raster
	p = inputRaster.rfind(".")
	outTMP = inputRaster[:p]
	outTMP = outTMP + "_TMPraster.tif"
	outDrv = gdal.GetDriverByName("GTiff")
	out = outDrv.Create(outTMP, cols, rows, 1, GDT_UInt16)
	out.SetProjection(ds.GetProjection())
	out.SetGeoTransform(ds.GetGeoTransform())
	rb_out = out.GetRasterBand(1)
	# Process the raster
	for y in range(rows):
		in_rb = rb.ReadAsArray(0,y,cols,1)
		dataOut = np.zeros((1,cols))
		np.putmask(dataOut, in_rb != RasterValue, 0)
		np.putmask(dataOut, in_rb == RasterValue, 1)
		rb_out.WriteArray(dataOut, 0, y)
	ds = None
	out = None
	# (2) Calculate Euclidean Distance to the non-forest-values
	command = "c:/python32/python.exe E:/kirkdata/mbaumann/GDAL_Executables/gdal_proximity.py " + outTMP + " " + outputRaster + " -q -values 1"
	os.system(command)
	# (3) Remove the TMP-file
	p = outTMP.rfind("/")
	folder = outTMP[:p+1]
	list = os.listdir(folder)
	try:
		os.remove(outTMP)
	except: print("Could remove file, please try manually, file:")
			print(outTMP)

# Calculate Euclidean Distance to elements (point, polygon, line) in a Vector-File
def DistanceToVectorFile(polygonFile, extentFile, idField, outputFile): # OutPut file type has to be GTiff
	print("Calculate Distance to Vector File")
	# (1) Get the Extent for the output-File
	ds = gdal.Open(extentFile)
	gt = ds.GetGeoTransform()
	cols = ds.RasterXSize
	rows = ds.RasterYSize
	pixelSize = gt[1]
	ext = []
	xarr = [0,cols]
	yarr = [0,rows]
	for px in xarr:
		for py in yarr:
			x = gt[0] + (px*gt[1])+(py*gt[2])
			y = gt[3] + (px*gt[4])+(py*gt[5])
			ext.append([x,y])
		yarr.reverse()
	ds = None
	# (2) Convert the vector-file to raster based on the ID-field
	outTMP = polygonFile
	outTMP = outTMP.replace(".shp","_TMPraster.tif")
	#command = "gdal_rasterize -a " + idField + " -tr " + str(pixelSize) + " " + str(pixelSize) + " -ot UInt16 -q -of GTiff -te " + str((ext[1][0])) + " " + str((ext[1][1])) + " " + str((ext[2][0])) + " " + str((ext[0][1])) + " " + polygonFile + " " + outTMP
	command = "gdal_rasterize -a " + idField + " -tr " + str(pixelSize) + " " + str(pixelSize) + " -q -of GTiff -te " + str((ext[1][0])) + " " + str((ext[1][1])) + " " + str((ext[2][0])) + " " + str((ext[0][1])) + " " + polygonFile + " " + outTMP
	os.system(command)
	# (3) Calculate Euclidean Distance to vector(raster)layer
	command = "c:/python32/python.exe E:/kirkdata/mbaumann/GDAL_Executables/gdal_proximity.py -q " + outTMP + " " + outputFile + " -distunits GEO"
	os.system(command)
	# (4) Delete the TMP-file
	p = outTMP.rfind("/")
	folder = outTMP[:p+1]
	list = os.listdir(folder)
	os.remove(outTMP)	
# Point Intersection. Get Information of layer at point locations of point-input-file. SpatialReferences do not have to be homogenized
# Vector-layer-TUPEL-input --> [LAYER_PATH, VarName_in_OutputTable, FieldInVector_ToBe_Extracted]
# Raster-Layer-TUPEL-input --> [LAYER_PATH, VarName_in_OutputTable]
# Tupels in 'layerList_tupel' need format: [[tupel01],[tupel02],...,[tupel_n]]
def PointIntersect(point_File, id_Field, layerList_tupel, output_csv):
	# (0) Create empty list for fields we will have at the end
	field_list = []
	# (1) Create lists for the ID-field in the shapefile
	points = ogr.Open(point_File)
	lyr = points.GetLayer()
	IDs = []
	IDs.append(id_Field)
	feature = lyr.GetNextFeature()
	while feature:
		id = feature.GetField(id_Field)
		IDs.append(id)
		feature = lyr.GetNextFeature()
	lyr.ResetReading()
	field_list.append(IDs)
	# (2) Now loop through all the layers and get the values --> check if raster or shapefile
	for layer in layerList_tupel[:]:
		name = layer[0]
		print(name)
	# (2a) Test if shp-file and process then
		if name.find(".shp") >= 0:
			variable_list = []
			variable_list.append(layer[1])
			fieldOfInterest = layer[2]
			# Load the polygon shape file and get the spatial reference, build coordinate transformation
			pols = ogr.Open(layer[0])
			pol_lyr = pols.GetLayer()
			target_SR = pol_lyr.GetSpatialRef()
			source_SR = lyr.GetSpatialRef()
			coordTrans = osr.CoordinateTransformation(source_SR, target_SR)
			# Go through each point and extract the value of the field of interest
			for feat in lyr:
				geom = feat.GetGeometryRef()
				geom.Transform(coordTrans)
				mx, my = geom.GetX(), geom.GetY()
				# Create a virtual point
				pt = ogr.Geometry(ogr.wkbPoint)
				pt.SetPoint_2D(0,mx,my)
				# Set up a spatial filter for polygon layer based on that point location
				pol_lyr.SetSpatialFilter(pt)
				for feat_in in pol_lyr:
					val = feat_in.GetFieldAsString(fieldOfInterest)
				if not val:
					variable_list.append("NaN")
				else:
					variable_list.append(val)
				val = None
				pol_lyr.ResetReading()
			lyr.ResetReading()
			field_list.append(variable_list)
		# (2b) If not a shape, then its a raster, process now
		else:
			# Create list for values to appended to overall list
			variable_list = []
			variable_list.append(layer[1])
			# Now load the raster and get necessary information
			ds = gdal.Open(layer[0])
			gt = ds.GetGeoTransform()
			pr = ds.GetProjection()
			ds_rb = ds.GetRasterBand(1)
			# Important --> define datatype for extraction below
			types = [[1,'b'], [2,'H'], [3,'h'], [4,'I'], [5,'i'],[6,'f'],[7,'d']]
			dataType = ds_rb.DataType
			for type in types:
				if type[0] == dataType:
					outType = type[1]
			target_SR = osr.SpatialReference()
			target_SR.ImportFromWkt(pr)
			# Now get the information from the point file and define the transformation
			source_SR = lyr.GetSpatialRef()
			coordTrans = osr.CoordinateTransformation(source_SR, target_SR)
			# Go through each point and extract the value
			for feat in lyr:
				geom = feat.GetGeometryRef()
				geom.Transform(coordTrans)
				mx, my = geom.GetX(), geom.GetY()
				px = int((mx - gt[0]) / gt[1])
				py = int((my - gt[3]) / gt[5])
				structval = ds_rb.ReadRaster(px,py,1,1)
				intval = struct.unpack(outType, structval)
				variable_list.append(intval[0])
			lyr.ResetReading()
			field_list.append(variable_list)
	
	# (3) Write into output-csv
	outlist = zip(*field_list)
	with open(output_csv, "w") as the_file:
		csv.register_dialect("custom", delimiter = ",", skipinitialspace = True, lineterminator='\n')
		writer = csv.writer(the_file, dialect="custom")
		for element in outlist:
			writer.writerow(element)
# Get NDVI-values at point-locations from landsat. "LandsatPath_list" requires entire file-paths to image		
def GetNDVIvaluesFromLandsatList(point_input, LandsatPath_list, csv_output):
	# (1) Initialize output-list
	field_list = []
	# (2) Open Point_Layer
	points = ogr.Open(point_input)
	lyr = points.GetLayer()
	feature = lyr.GetNextFeature()
	# (3) Build ID-Column for Output-Layer
	id_list = []
	id_list.append("Point-ID")
	id = 1
	while feature:
		id_list.append(id)
		id = id + 1
		feature = lyr.GetNextFeature()
	lyr.ResetReading()
	field_list.append(id_list)
	# (4) Now loop through each of the Landsat-NDVI-images and extract the NDVI-value
	for path in LandsatPath_list[:]:
		# (a) Establish list for values and give it column name
		val_list = []
		p = path.rfind("/")
		sceneID = path[p+1:len(path)]
		val_list.append(sceneID)
		# Open the raster and get information about datatype --> makes it non-vulnerable to pre-processing degrees (DN, TOA, SF)
		ds = gdal.Open(path)
		gt = ds.GetGeoTransform()
		pr = ds.GetProjection()
		ds_band3 = ds.GetRasterBand(3)
		ds_band4 = ds.GetRasterBand(4)
		types = [[1,'b'], [2,'H'], [3,'h'], [4,'I'], [5,'i'],[6,'f'],[7,'d']]
		dataType = ds_band3.DataType
		for type in types:
			if type[0] == dataType:
				outType = type[1]
		# Define coordinate transformation --> makes it non-vulnerable to different coordinate systems of layers
		target_SR = osr.SpatialReference()
		target_SR.ImportFromWkt(pr)
		source_SR = lyr.GetSpatialRef()
		coordTrans = osr.CoordinateTransformation(source_SR, target_SR)
		# Now loop over each point, get b3/b4 values and calculate NDVI
		for feat in lyr:
			geom = feat.GetGeometryRef()
			geom.Transform(coordTrans)
			mx, my = geom.GetX(), geom.GetY()
			px = int((mx - gt[0]) / gt[1])
			py = int((my - gt[3]) / gt[5])
			B3_struct = ds_band3.ReadRaster(px,py,1,1)
			B3 = struct.unpack(outType, B3_struct)
			B3 = B3[0]
			B4_struct = ds_band4.ReadRaster(px,py,1,1)
			B4 = struct.unpack(outType, B4_struct)
			B4 = B4[0]
			ndvi = (B4-B3)/(B4+B3)
			val_list.append(ndvi)
		lyr.ResetReading()
		field_list.append(val_list)
	# (5) Write Output-file
	outlist = zip(*field_list)
	with open(csv_output, "w") as the_file:
		csv.register_dialect("custom", delimiter = ",", skipinitialspace = True, lineterminator='\n')
		writer = csv.writer(the_file, dialect="custom")
		for element in outlist:
			writer.writerow(element)
# Get Information about Fmask-value at point-locationa cross Fmasks
def GetFmaskInfoFromLandsatList(point_input, LandsatPath_list, csv_output):
	# (1) Initialize output-list
	field_list = []
	# (2) Open Point_Layer
	points = ogr.Open(point_input)
	lyr = points.GetLayer()
	feature = lyr.GetNextFeature()
	# (3) Build ID-Column for Output-Layer
	id_list = []
	id_list.append("Point-ID")
	id = 1
	while feature:
		id_list.append(id)
		id = id + 1
		feature = lyr.GetNextFeature()
	lyr.ResetReading()
	field_list.append(id_list)
	# (4) Now loop through each of the Landsat-NDVI-images and extract the NDVI-value
	for path in LandsatPath_list[:]:
		# (a) Establish list for values and give it column name
		val_list = []
		p = path.rfind("/")
		sceneID = path[p+1:len(path)]
		val_list.append(sceneID)
		# Open the raster and get information about datatype --> makes it non-vulnerable to pre-processing degrees (DN, TOA, SF)
		ds = gdal.Open(path)
		gt = ds.GetGeoTransform()
		pr = ds.GetProjection()
		ds_band1 = ds.GetRasterBand(1)
		types = [[1,'b'], [2,'H'], [3,'h'], [4,'I'], [5,'i'],[6,'f'],[7,'d']]
		dataType = ds_band1.DataType
		for type in types:
			if type[0] == dataType:
				outType = type[1]
		# Define coordinate transformation --> makes it non-vulnerable to different coordinate systems of layers
		target_SR = osr.SpatialReference()
		target_SR.ImportFromWkt(pr)
		source_SR = lyr.GetSpatialRef()
		coordTrans = osr.CoordinateTransformation(source_SR, target_SR)
		# Now loop over each point, get b3/b4 values and calculate NDVI
		for feat in lyr:
			geom = feat.GetGeometryRef()
			geom.Transform(coordTrans)
			mx, my = geom.GetX(), geom.GetY()
			px = int((mx - gt[0]) / gt[1])
			py = int((my - gt[3]) / gt[5])
			obs_struct = ds_band1.ReadRaster(px,py,1,1)
			obs = struct.unpack(outType, obs_struct)
			obs = obs[0]
			val_list.append(obs)
		lyr.ResetReading()
		field_list.append(val_list)
	# (5) Write Output-file
	outlist = zip(*field_list)
	with open(csv_output, "w") as the_file:
		csv.register_dialect("custom", delimiter = ",", skipinitialspace = True, lineterminator='\n')
		writer = csv.writer(the_file, dialect="custom")
		for element in outlist:
			writer.writerow(element)			
# Re-Project Raster/Vector to a different coordinate system.
# out_projection can be a file, from which coordinate system is taken, or can be given as EPSG (spatialreference.org). E.g."EPSG:4326"
def ReprojectionTool(input_file, output_file, out_projection):
	# Test if the input-file is a shapefile
	if input_file.find(".shp") >= 0:
		# Test if out-projection comes from a file or is defined as EPSG-Notation
		if out_projection.find("EPSG") >= 0:
			command = "ogr2ogr -t_srs " + out_projection + " " + output_file + " " + input_file
			os.system(command)
		# If EPSG is not given then we get the projection from a reference file
		# (a) Check if it is a shapefile
		if out_projection.find(".shp") >= 0:
			ds = ogr.Open(out_projection)
			lyr = ds.GetLayer()
			ref = lyr.GetSpatialRef()
			target_SR = ref.ExportToWkt()
			command = "ogr2ogr -t_srs " + target_SR + " " + output_file + " " + input_file
			os.system(command)
		# (b) if it is not a shapefile, then it is a rasterfile
		else:
			ds = gdal.Open(out_projection)
			pr = ds.GetProjection()
			command = "ogr2ogr -t_srs " + pr + " " + output_file + " " + input_file
			os.system(command)
	# If input-file is not a shapefile, then it is a rasterfile
	else:
		# Test if out-projection comes from a file, or is defined as EPSG-Notation
		if out_projection.find("EPSG") >= 0:
			command = "gdalwarp -q -r cubic -t_srs " + out_projection + " " + input_file + " " + output_file
			os.system(command)
		# If EPSG is not given then we get the projection from a reference file
		# (a) Check it is a shapefile
		if out_projection.find(".shp") >= 0:
			ds = ogr.Open(out_projection)
			lyr = ds.GetLayer()
			ref = lyr.GetSpatialRef()
			target_SR = ref.ExportToWkt()
			command = "gdalwarp -q -r cubic -t_srs " + target_SR + " " + input_file + " " + output_file
			os.system(command)
		# (b) if it is not a shapefile, then it is a rasterfile
		else:
			ds = gdal.Open(out_projection)
			pr = ds.GetProjection()
			command = "gdalwarp -q -r cubic -t_srs " + pr + " " + input_file + " " + output_file
			os.system(command)
# Homogenize Coordinate System of multiple files (given as list with full paths). Target_SRS either as EPSG or from file.
# Raster will be re-projected using Cubic Convolution, Extension is a string to show for the file ending that it is projected, e.g. "_UTM44N"
def HomogenizeCoordinateSystems(input_list, target_SRS, Extension):
	# Check, if target-SRS comes from file or from EPSG
	if target_SRS.find("EPSG") >= 0:
		# Loop through each file of the input-list
		for file in input_list[:]:
			print(file)
			# (a) Check if "file" is a shapefile
			if file.find(".shp") >= 0:
				input = file
				output = file
				output = output.replace(".",Extension+".")
				command = "ogr2ogr -t_srs " + target_SRS + " " + output + " " + input
				os.system(command)
			# (b) it it is not a shapefile, it is a raster
			else:
				input = file
				output = file
				output = output.replace(".",Extension+".")
				command = "gdalwarp r- cubic -q -t_srs " + target_SRS + " " + input + " " + output
				os.system(command)
	# Check if target-SRS comes from a shapefile
	if target_SRS.find(".shp") >= 0:
		# Build the spatial reference
		ds = ogr.Open(out_projection)
		lyr = ds.GetLayer()
		ref = lyr.GetSpatialRef()
		target_SR = ref.ExportToWkt()
		# Loop through each file of the input-list
		for file in input_list[:]:
			print(file)
			# (a) Check if "file" is a shapefile
			if file.find(".shp") >= 0:
				input = file
				output = file
				output = output.replace(".",Extension+".")
				command = "ogr2ogr -t_srs " + target_SR + " " + output + " " + input
				os.system(command)
			# (b) it it is not a shapefile, it is a raster
			else:
				input = file
				output = file
				output = output.replace(".",Extension+".")
				command = "gdalwarp r- cubic -q -t_srs " + target_SRS + " " + input + " " + output
				os.system(command)
	# If target-SRS is not from EPSG or from shapefile, it comes from a raster-file
	if target_SRS.find(".img") >= 0 or target_SRS.find(".tif") >= 0:
		ds = gdal.Open(target_SRS)
		target_SR = ds.GetProjection()
		# Loop through each file of the input-list
		for file in input_list[:]:
			print(file)
			# (a) Check if "file" is a shapefile
			if file.find(".shp") >= 0:
				input = file
				output = file
				output = output.replace(".",Extension+".")
				command = "ogr2ogr -t_srs " + target_SR + " " + output + " " + input
				os.system(command)
			# (b) it it is not a shapefile, it is a raster
			else:
				input = file
				output = file
				output = output.replace(".",Extension+".")
				command = "gdalwarp r- cubic -q -t_srs " + target_SR + " " + input + " " + output
				os.system(command)
# Extract values to points from MODIS-time series. MODIS-file have to be in one folder, converted into GTiff
# Function is independent of coordinate systems (internal conversion before extracting values)
def ExtractValuesFromMODISseries(input_folder, point_file, output_csv):
	# Establish final outlist, to which remaining list get appended
	outlist = []
	# Establish List with headers, we need point-number for that
	headerList = ['Date', 'Year', 'DOY']
	points = ogr.Open(point_file)
	lyr = points.GetLayer()
	feature = lyr.GetNextFeature()
	id = 1
	while feature:
		varName = "Point_" + str(id)
		headerList.append(varName)
		id = id + 1
		feature = lyr.GetNextFeature()
	lyr.ResetReading()
	outlist.append(headerList)
	# Loop through the input-folder and extract the values
	raster_list = [f for f in os.listdir(input_folder) if f.endswith('.tif')]
	for raster in raster_list:
		print(raster)
		# Initiate list, which we populate
		values = []
		# Get the infos for 'Date', 'Year' & 'DOY'
		p = raster.find(".")
		d = raster[p+2:p+9]
		d = d[0:4] + "-" + d[4:int(len(d))]
		values.append(d)
		y = int(d[0:4])
		values.append(y)
		dy = int(d[5:int(len(d))])
		values.append(dy)
		# Now get the raster-value for each point in the feature-file
		# (a) Open the raster-file, get information about Projection and DataType
		ds = gdal.Open(input_folder + raster, GA_ReadOnly)
		gt = ds.GetGeoTransform()
		pr = ds.GetProjection()
		ds_rb = ds.GetRasterBand(1)
		# Important --> define datatype for extraction below
		types = [[1,'b'], [2,'H'], [3,'h'], [4,'I'], [5,'i'],[6,'f'],[7,'d']]
		dataType = ds_rb.DataType
		for type in types:
			if type[0] == dataType:
				outType = type[1]
		target_SR = osr.SpatialReference()
		target_SR.ImportFromWkt(pr)
		# (b) Get from point-file information about the coordinatesystem of the point-file, generate coordinate-transformation
		source_SR = lyr.GetSpatialRef()
		coordTrans = osr.CoordinateTransformation(source_SR, target_SR)
		# (c) Loop through each point(feature) of the point-layer, extract value
		for feat in lyr:
			geom = feat.GetGeometryRef()
			geom.Transform(coordTrans)
			mx, my = geom.GetX(), geom.GetY()
			px = int((mx - gt[0]) / gt[1])
			py = int((my - gt[3]) / gt[5])
			structval = ds_rb.ReadRaster(px,py,1,1)
			intval = struct.unpack(outType, structval)
			values.append(intval[0])
		lyr.ResetReading()
		outlist.append(values)
	# Write everything out into the output-csv
	with open(output_csv, "w") as the_file:
		csv.register_dialect("custom", delimiter=",", skipinitialspace=True, lineterminator='\n')
		writer = csv.writer(the_file, dialect="custom")
		for element in outlist:
			writer.writerow(element)


				
# Other stuff to include:
# 1. simple random sample (vector)
# 2. intersect/dissolve			
# 3. Count Points in polygon
# 4. join csv to shapefile
# 5. Mosaic raster
# 6. calculate Area for polygon-file
# 7. Make ZonalStats more comfortable --> in a similar fashion as the PointIntersecttool is


