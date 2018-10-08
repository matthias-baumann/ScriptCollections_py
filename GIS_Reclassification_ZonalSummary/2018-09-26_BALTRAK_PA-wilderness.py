# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import ogr, gdal, osr
import baumiTools as bt
from tqdm import tqdm
import numpy as np
import random
import struct
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ############################################################################################################# #
workFolder = "Y:/Baumann/BALTRAK/Connectivity/"
shapeFolder = "D:/Research/Publications/Publications-in-preparation/baumann-etal_LandUseChange-Wilderness_Kostanay-KZ/Shapefiles/Summary_Shapes/"
PA15 = bt.baumiVT.CopyToMem(shapeFolder + "PA_2015.shp")
outputFile = "D:/Research/Publications/Publications-in-preparation/baumann-etal_LandUseChange-Wilderness_Kostanay-KZ/____PA_summaries.csv"
#random.seed(1) # for reproducability of the results
nPoints = 100
bufferStep = 3000
maxBuff = 99000
# ####################################### FUNCTIONS ########################################################### #
def CalcSummaries(valList, buffer):
	np_values = np.array(valList)
	mean = np.ma.mean(np_values)
	min = np.ma.min(np_values)
	max = np.ma.max(np_values)
	sd = np.ma.std(np_values)
	median = np.median(np_values)
	p25 = np.percentile(np_values, 25)
	p75 = np.percentile(np_values, 75)
	iqr = p75 - p25
	up_whisk = np_values[np_values <= p75 + 1.5 * iqr].max()
	lo_whisk = np_values[np_values >= p25 - 1.5 * iqr].min()
	outList = [PAname, PAcat, PAyear, PAperiod, PAinside, buffer, mean, sd, min, lo_whisk, p25, median, p75, up_whisk, max, layer, th, yr]
	return outList

# ####################################### LOOP THROUGH FEATURES ############################################### #
#### (1) DEFINE THE NAMES FOR THE RASTER-FILES
allRasters = [#["SUM", "1990", "NN", "01_Layer-SUM/SUM_Wilderness_1990.tif"],
              #["SUM", "2015", "th10", "01_Layer-SUM/SUM_Wilderness_2015_th10.tif"],
              #["SUM", "2015", "th50", "01_Layer-SUM/SUM_Wilderness_2015_th50.tif"],
              #["SUM", "2015", "th90", "01_Layer-SUM/SUM_Wilderness_2015_th90.tif"],
              #["SUM", "2015-1990", "th10", "01_Layer-SUM/SUM_Wilderness_2015-1990_th10.tif"],
              #["SUM", "2015-1990", "th50", "01_Layer-SUM/SUM_Wilderness_2015-1990_th50.tif"],
              #["SUM", "2015-1990", "th90", "01_Layer-SUM/SUM_Wilderness_2015-1990_th90.tif"],
              ["PRODUCT", "1990", "NN", "02_Layer-PRODUCT/PRODUCT_Wilderness_1990.tif"],
              ["PRODUCT", "2015", "th10", "02_Layer-PRODUCT/PRODUCT_Wilderness_2015_th10.tif"],
              ["PRODUCT", "2015", "th50", "02_Layer-PRODUCT/PRODUCT_Wilderness_2015_th50.tif"],
              ["PRODUCT", "2015", "th90", "02_Layer-PRODUCT/PRODUCT_Wilderness_2015_th90.tif"],
              ["PRODUCT", "2015-1990", "th10", "02_Layer-PRODUCT/PRODUCT_Wilderness_2015-1990_th10.tif"],
              ["PRODUCT", "2015-1990", "th50", "02_Layer-PRODUCT/PRODUCT_Wilderness_2015-1990_th50.tif"],
              ["PRODUCT", "2015-1990", "th90", "02_Layer-PRODUCT/PRODUCT_Wilderness_2015-1990_th90.tif"]]#,
              #["MIN", "1990", "NN", "03_Layer-MIN/MIN_Wilderness_1990.tif"],
              #["MIN", "2015", "th10", "03_Layer-MIN/MIN_Wilderness_2015_th10.tif"],
              #["MIN", "2015", "th50", "03_Layer-MIN/MIN_Wilderness_2015_th50.tif"],
              #["MIN", "2015", "th90", "03_Layer-MIN/MIN_Wilderness_2015_th90.tif"],
              #["MIN", "2015-1990", "th10", "03_Layer-MIN/MIN_Wilderness_2015-1990_th10.tif"],
              #["MIN", "2015-1990", "th50", "03_Layer-MIN/MIN_Wilderness_2015-1990_th50.tif"],
              #["MIN", "2015-1990", "th90", "03_Layer-MIN/MIN_Wilderness_2015-1990_th90.tif"]]

# # (2) LOOP THROUGH PROTECTED AREAS
outTab = [["PA_Name", "Kaz_Cat", "Year", "Period", "Inside_YN", "Buffer", "Mean", "SD", "Min", "Lower_whisker", "Q25", "Median", "Q75", "Upper_whisker", "Max", "RasterLayer", "Threshold", "Year"]]
lyr = PA15.GetLayer()
# Make a selection
lyr.SetAttributeFilter("Name NOT IN ('Turgaiskii Zakaznik', 'Irgiz-Turgay State Nature Reserve', 'Tengiz-Korgalzhynskii Gosudarstvennyi Zapovednik - Extension')")
feat = lyr.GetNextFeature()
while feat:
	PAname = feat.GetField("Name")
	print(PAname)
	PAcat = feat.GetField("Kaz_Cat")
	PAyear = feat.GetField("Year")
	PAperiod = feat.GetField("Period")
	PAinside = feat.GetField("IN_yn")
# Loop through the rasters and generate samples for each raster and calculate the statistics
	for ras in allRasters:
	# Extract the information from the list from above
		layer = ras[0]
		yr = ras[1]
		th = ras[2]
		ds = ras[3]
	# Open the raster file and get GeoInformation
		ds_open = gdal.Open(workFolder + ds)
		gt = ds_open.GetGeoTransform()
		pr = ds_open.GetProjection()
		rb = ds_open.GetRasterBand(1)
		dType = bt.baumiRT.GetDataTypeHexaDec(rb.DataType)
	# (1) Calculate the Wilderness and connectivity inside the PAs --> only if IN_yn == 1
		if not PAinside == 1:
			outTab.append([PAname, PAcat, PAyear, PAperiod, PAinside, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, layer, th, yr])
		else:
		# Get the geometry and extent
			geomPA = feat.GetGeometryRef()
			ext = geomPA.GetEnvelope()
		# Generate a random pair of coordinates within the extent of the geometry, build geometry
			n = 1
			values = []
			while n <= nPoints:
				x_sample = random.uniform(ext[0], ext[1])
				y_sample = random.uniform(ext[2], ext[3])
				geomPoint = ogr.Geometry(ogr.wkbPoint)
				geomPoint.AddPoint(x_sample, y_sample)
				#print(geomPoint)
				#print(geomPA)
			# Check if the point is in the shpLYR, if yes, then get the raster-value
				intersect = geomPA.Intersection(geomPoint)
				#print(intersect)
				if intersect.ExportToWkt() != 'GEOMETRYCOLLECTION EMPTY':
					px = int((x_sample - gt[0]) / gt[1])
					py = int((y_sample - gt[3]) / gt[5])
					structVar = rb.ReadRaster(px, py, 1, 1)
					val = struct.unpack(dType, structVar)[0]
					values.append(val)
					n += 1
		# Once we have 100 values in the list, calculate the statistics, append to output
			outTab.append(CalcSummaries(values, 0))
	# (2) Calculate the Wilderness and connectivity outside the PAs --> in 1km buffers
		buff = bufferStep
		while buff <= maxBuff:
			geomBuff = geomPA.Buffer(buff)
			geomBuff_only = geomBuff.Difference(geomPA)
			extBuff = geomBuff_only.GetEnvelope()
			n = 1
			values = []
			while n <= nPoints:
				x_sample = random.uniform(extBuff[0], extBuff[1])
				y_sample = random.uniform(extBuff[2], extBuff[3])
				geomPoint = ogr.Geometry(ogr.wkbPoint)
				geomPoint.AddPoint(x_sample, y_sample)
				# Check if the point is in the shpLYR, if yes, then get the raster-value
				intersect = geomBuff_only.Intersection(geomPoint)
				# print(intersect)
				if intersect.ExportToWkt() != 'GEOMETRYCOLLECTION EMPTY':
					px = int((x_sample - gt[0]) / gt[1])
					py = int((y_sample - gt[3]) / gt[5])
					structVar = rb.ReadRaster(px, py, 1, 1)
					val = struct.unpack(dType, structVar)[0]
					values.append(val)
					n += 1
			# Calculate statistics, add to output and increase buffer
			#bt.baumiVT.SaveGEOMtoFile(geomBuff_only, "D:/test.shp")
			#exit(0)
			outTab.append(CalcSummaries(values, buff))
			buff = buff + bufferStep
	# (3) Get the next protected area
	feat = lyr.GetNextFeature()
bt.baumiFM.WriteListToCSV(outputFile, outTab, delim=",")
# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")