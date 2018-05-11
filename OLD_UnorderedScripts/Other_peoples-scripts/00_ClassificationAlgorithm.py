# ######################################## LOAD REQUIRED MODULES ############################################### #
import os, sys
import time, datetime
import ogr, osr
import gdal
from gdalconst import *
import numpy as np
import csv
import itertools
import math
import scipy.ndimage
import struct
# below is all SVM-stuff
from sklearn import svm
from sklearn import grid_search
from sklearn.cross_validation import train_test_split
from sklearn.grid_search import GridSearchCV
from sklearn.metrics import classification_report
from sklearn.svm import SVC
from sklearn import preprocessing
from sklearn import metrics
# ####################################### SET TIME-COUNT ######################################################## #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:", starttime)
print("")

# ####################################### SET HARD CODED FOLDER PATHS AND SHP-FILE INPUTS ####################### #
TrainingPoints = "E:/kirkdata/mbaumann/Species-separation_Chapter03/09_PostWarping_Classification_SinglePoints/01_184018L5L7on8img_ClassificationSamples_5classes.shp"
ValidationPoints = "E:/kirkdata/mbaumann/Species-separation_Chapter03/09_PostWarping_Classification_SinglePoints/01_184018L5L7on8img_ValidationSamples_5classes.shp"
ImageInventory = "E:/kirkdata/mbaumann/Species-separation_Chapter03/09_PostWarping_Classification_SinglePoints/02_WellDistributed_TimeSeries_FP184018only_ALL_19-images.txt"
Landsat184018 = "E:/kirkdata/mbaumann/Landsat_Processing/Landsat/184018/"
output_csv = "E:/kirkdata/mbaumann/Species-separation_Chapter03/09_PostWarping_Classification_SinglePoints/01_Point-Accuracies.csv"
# ######################################## BUILD GLOBAL FUNCTIONS ############################################### #

def GetImageInventory(InventoryList, FP_folder):
	images = []
	invenOpen = open(InventoryList, "r")
	for line in invenOpen:
		if line.find("\n") >= 0:
			line = line.replace("\n","")
			path = FP_folder + line + "/" + line
			images.append(path)
	invenOpen.close()
	return images

def BuildHeaderList(imageList, class_list):
	headerList = ["Classif-#"]
	for img in imageList:
		p = img.rfind("/")
		imgID = img[p+1:len(img)]
		headerList.append(imgID)
	headerList.append("Over.Acc.")
	headerList.append("Kappa")
	for clas in class_list:
		ua = "UA_" + str(clas)
		pa = "PA_" + str(clas)
		headerList.append(ua)
		headerList.append(pa)
	return(headerList)
	
def GetPointLabels(shapefile, id_field, IntClass_field):
	IDs = []
	labels = []
	ds = ogr.Open(shapefile)
	lyr = ds.GetLayer()
	feature = lyr.GetNextFeature()
	while feature:
		id = feature.GetField(id_field)
		lab = feature.GetField(IntClass_field)
		IDs.append(id)
		labels.append(lab)
		feature = lyr.GetNextFeature()
	lyr.ResetReading()
	ds.Destroy()
	return IDs, labels

def BuildImageCombinations(combination, imageList):
	comboImages = []
	for i in range(0,len(combination)):
		active = combination[i]
		if active > 0:
			comboImages.append(imageList[i])
	return comboImages

def ExtractSpectralValues(pointFile,imageList):
	# Establish output-list
	data = []
	# Open the point layer
	ds = ogr.Open(pointFile)
	lyr = ds.GetLayer()
	point_SR = lyr.GetSpatialRef()
	# Start looping through the features in pointFile
	for feat in lyr:
		# Establish list for spectral values of this feature
		specVal = []
		# Now loop through each image file, extract spectral values at point
		for image in imageList:
			# Open the raster, perform on-the-fly coordinate transformation
			img = gdal.Open(image, GA_ReadOnly)
			nr_bands = img.RasterCount
			gt = img.GetGeoTransform()
			pr = img.GetProjection()
			raster_SR = osr.SpatialReference()
			raster_SR.ImportFromWkt(pr)
			coordTrans = osr.CoordinateTransformation(point_SR, raster_SR)
			# Get point coordinates
			geom = feat.GetGeometryRef()
			geom.Transform(coordTrans)
			mx, my = geom.GetX(), geom.GetY()
			px = int((mx - gt[0]) / gt[1])
			py = int((my - gt[3]) / gt[5])
			# Now loop through each band
			for b in range(1,nr_bands+1): # nr_bands+1 because of zero-based counting
				band = img.GetRasterBand(b)
				# Check for file-format and define structval
				types = [[1,'b'], [2,'H'], [3,'h'], [4,'I'], [5,'i'],[6,'f'],[7,'d']]
				dataType = band.DataType
				for type in types:
					if type[0] == dataType:
						outType = type[1]
				# Read Out the raster value and append to specVal-List
				structval = band.ReadRaster(px, py, 1, 1)
				intval = struct.unpack(outType , structval)
				specVal.append(intval[0])
		# Append values of the point to overall training file
		data.append(specVal)
	# Scale the data between 0 and 1 for SVM-classification
	data = np.array(data)
	data = data.astype(np.float32, copy=False)
	min_max_scaler = preprocessing.MinMaxScaler()
	data = min_max_scaler.fit_transform(data)
	lyr.ResetReading()
	ds.Destroy()
	return data

def CalculateAccuracy(confusionMatrix):
	accuracyList = []
	# NaN might be generated, with the warning function we are not getting popped out
	import warnings
	warnings.simplefilter("ignore", RuntimeWarning) 
	# Calculate summaries for Overall accuracy and 
	sum_diag = sum(np.diagonal(Conf_matrix))		# Sum of Diagonal
	ColSum = np.sum(confusionMatrix, axis = 0)			# Sum of Columns
	RowSum = np.sum(confusionMatrix, axis = 1)			# Sum of Rows
	ColSumRowSum = np.dot(ColSum, RowSum)			# Sum of col-sum X row-sum
	sum_ALL = np.sum(confusionMatrix)					# Number of points in Accuracy Assessment
	# Calculate Overall Accuracy and Kappa statistics
	OA = sum_diag / sum_ALL
	accuracyList.append(OA)
	kappa = (sum_ALL * sum_diag - ColSumRowSum) / (sum_ALL * sum_ALL - ColSumRowSum)
	accuracyList.append(kappa)
	# Calculate Users and producers accuracies
	matrixDim = confusionMatrix.shape
	for i in range(0,matrixDim[1]):
		# Calculate for each class the user's and producer's accuracy, append to accuracyList
		UA = confusionMatrix[i,i] / RowSum[i]
		accuracyList.append(UA)
		PA = confusionMatrix[i,i] / ColSum[i]
		accuracyList.append(PA)
	return accuracyList

def TestIfAllClearObs(pointFile, imageList):
	# Establish output-list
	data = []
	# Open the point layer
	ds = ogr.Open(pointFile)
	lyr = ds.GetLayer()
	point_SR = lyr.GetSpatialRef()
	# Start looping through the features in pointFile
	for feat in lyr:
		# Now loop through each image file, extract spectral values at point
		for image in imageList:
			# Modify the path to access the Fmask 
			modPath = image + "_MTLFmask"
			# Open the raster, perform on-the-fly coordinate transformation
			img = gdal.Open(modPath, GA_ReadOnly)
			nr_bands = img.RasterCount
			gt = img.GetGeoTransform()
			pr = img.GetProjection()
			raster_SR = osr.SpatialReference()
			raster_SR.ImportFromWkt(pr)
			coordTrans = osr.CoordinateTransformation(point_SR, raster_SR)
			# Get point coordinates
			geom = feat.GetGeometryRef()
			geom.Transform(coordTrans)
			mx, my = geom.GetX(), geom.GetY()
			px = int((mx - gt[0]) / gt[1])
			py = int((my - gt[3]) / gt[5])
			# Now loop through each band
			band = img.GetRasterBand(1)
			# Check for file-format and define structval
			types = [[1,'b'], [2,'H'], [3,'h'], [4,'I'], [5,'i'],[6,'f'],[7,'d']]
			dataType = band.DataType
			for type in types:
				if type[0] == dataType:
					outType = type[1]
				# Read Out the raster value and append to specVal-List
			structval = band.ReadRaster(px, py, 1, 1)
			intval = struct.unpack(outType , structval)
			data.append(intval[0])
	data = list(data)
	lyr.ResetReading()
	ds.Destroy()
	return data
	
# ############################################################################################################### #	
# (1) READ IN IMAGE LISTS AND BUILD IMAGE-COMBINATIONS
imageList = GetImageInventory(ImageInventory,Landsat184018)
combos = []
for i in itertools.product(range(2), repeat = len(imageList)):
	if sum(i) > 0:
		combos.append(i)

# (2) INITIALIZE OUTPUT-LIST, FIRST LIST WILL BE COLUMN NAMES --> check class-names prior to that
output_list = []
headerList = BuildHeaderList(imageList, [100,200,2000,2100,2200])
output_list.append(headerList)

# (3) LOAD THE POINT SHP FILES AND BUILD LISTS WITH IDs AND LABELS	
TD = GetPointLabels(TrainingPoints, "Id","Class")
TD_id, TD_labels = TD[0], TD[1]
VD = GetPointLabels(ValidationPoints, "Id","Class")
VD_id, VD_labels = VD[0], VD[1]

# (4) LOOP THROUGH THE IMAGE COMBINATIONS AND PERFORM THE CLASSIFICATION/VALIDATION
# (4-1) Establish loop
for combo in combos:
	classResultList = []
	comboID = combos.index(combo) + 1
	classResultList.append(comboID) # For output-writing
	print("Classification", comboID, "from", len(combos))
	combo = list(combo)
	for c in combo: # For output-writing
		classResultList.append(c)
# (4-2) Select the images we need for the classification
	combo_images = BuildImageCombinations(combo, imageList)
# (4-3) Test if all used imagery actually have clear observations
	TD_clearObstest = TestIfAllClearObs(TrainingPoints, combo_images)
	VD_clearObstest = TestIfAllClearObs(ValidationPoints, combo_images)
	if any(Obs > 0 for Obs in TD_clearObstest) or any(Obse > 0 for Obse in VD_clearObstest):
		print(combo, "has not clear observations in every image, skipping")
	else:
# (4-4) Generate training and validation data	
		TD_specValues = ExtractSpectralValues(TrainingPoints, combo_images)
		TD_labels_asArray = np.array(TD_labels)
		VD_specValues = ExtractSpectralValues(ValidationPoints, combo_images)
		VD_labels_asArray = np.array(VD_labels)
# (4-5) Fit the SVM-Model for training data and validate with Validation dataset
	# Set the C-gamma-range, and define kernel-type (here:rbf)
		tuning_parameters = [{'kernel': ['rbf'], 'gamma': [0.1, 1, 10, 100, 1000], 'C': [0.1, 1, 10, 100, 1000]}]		
	# Run the GRID-search
		svr = svm.SVC()
		clf = grid_search.GridSearchCV(svr, tuning_parameters, cv=3, score_func=metrics.accuracy_score)
		clf.fit(TD_specValues, TD_labels_asArray)
	# Predict the validation data
		y_true, y_pred = VD_labels_asArray, clf.predict(VD_specValues)
		Conf_matrix = metrics.confusion_matrix(y_pred, y_true)
# (4-6) Calculate the accuracy measures and append to classResultList
		accuracyList = CalculateAccuracy(Conf_matrix)
	# Append the values in the accuracyList to classResultList
		for val in accuracyList:
			classResultList.append(val)
	# Append Results from this classification to the overall output_list
		output_list.append(classResultList)
# (5) Write output csv-file
with open(output_csv, "w") as the_file:
	csv.register_dialect("custom", delimiter = ",", skipinitialspace = True, lineterminator='\n')
	writer = csv.writer(the_file, dialect="custom")
	for element in output_list:
		writer.writerow(element)

# ####################################### SET TIME-COUNT ######################################################## #
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: ", starttime)
print("end: ", endtime)
print("")