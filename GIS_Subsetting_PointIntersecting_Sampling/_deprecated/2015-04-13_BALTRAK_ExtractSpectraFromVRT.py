# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import os
import time
import gdal
import ogr, osr
from gdalconst import *
import struct
import numpy as np
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " +  starttime)
print("")
# ####################################### HARD-CODED FOLDERS AND FILES ######################################## #
shp_folder = "E:/Baumann/BALTRAK/01_ClassificationRuns/Run08/SHP/"
#shp_folder = "P:/BALTRAK/01_ClassificationRuns/Run05/SHP/"
mosaic_in = "E:/Baumann/BALTRAK/StackedTiles_VRT.vrt"
#mosaic_in = "P:/BALTRAK/StackedTiles_VRT.vrt"
out_spec = "E:/Baumann/BALTRAK/01_ClassificationRuns/Run08/Run08_TDSample_4000PointsPerClass_spectra.bsq"
#out_spec = "P:/BALTRAK/01_ClassificationRuns/Run05/Run05_TDSample_4000PointsPerClass_spectra.bsq"
out_label = "E:/Baumann/BALTRAK/01_ClassificationRuns/Run08/Run08_TDSample_4000PointsPerClass_labels.bsq"
#out_label = "P:/BALTRAK/01_ClassificationRuns/Run05/Run05_TDSample_4000PointsPerClass_labels.bsq"
labels = [["01_Forest",1],["02_Wetlands",2],["03_Water",3],["04_Other",4],["15_Wet-Agro",15],
          ["05_C-C-C",5],["06_C-G-G",6],["07_C-C-G",7],["C-G-C",11],
          ["08_G-G-G",8],["09_G-G-C",9],["10_G-C-C",10],["14_G-C-G",14],
          ["12_F-F-NF",12],["13_F-NF-NF",13]]
# ####################################### GLOBAL FUNCTIONS #################################################### #
def AddClassID(shp, clas):
	driver = ogr.GetDriverByName('ESRI Shapefile')
	points = driver.Open(shp, 1)
	fieldDefn = ogr.FieldDefn('Class', ogr.OFTInteger)
	lyr = points.GetLayer()
	lyr.CreateField(fieldDefn)
	feature = lyr.GetNextFeature()
	while feature:
		feature.SetField('Class', clas)
		lyr.SetFeature(feature)
		feature = lyr.GetNextFeature()
	lyr.ResetReading()
def MergeSHPfiles(listOfSHPfiles, shpOut):
	# Merge the temporary files into one single one
	for file in listOfSHPfiles:
		if not os.path.exists(shpOut):
			command = "ogr2ogr.exe " + shpOut + " " + file
			os.system(command)
		else:
			command = "ogr2ogr.exe -update -append " + shpOut + " " + file
			os.system(command)	
def GetFeatureCount(shp):
	lyr = shp.GetLayer()
	numFeat = lyr.GetFeatureCount()
	return numFeat
def GetNumberOfBands(raster):
	numBand = raster.RasterCount
	return numBand
def GetProfile(feature, coordTrans, raster, bands):
	outList = []
	for b in range(bands):
		gt = raster.GetGeoTransform()
		band = raster.GetRasterBand((b+1))
		geom = feature.GetGeometryRef()
		geom.Transform(coordTrans)
		mx, my = geom.GetX(), geom.GetY()
		px = int((mx - gt[0]) / gt[1])
		py = int((my - gt[3]) / gt[5])
		structval = band.ReadRaster(px,py,1,1)
		intval = struct.unpack('H', structval)
		outList.append(intval[0])
	return outList

# ####################################### START PROCESSING #################################################### #
# (1) ADD CLASS-LABEL TO SHAPEFILES AND MERGE
print("Add Class-Labels to shp and merge")
mergedShape = shp_folder + "00_TrainingData_merged.shp"
if not os.path.exists(mergedShape):
	shp_list = [shp_folder + shp for shp in os.listdir(shp_folder) if shp.endswith('.shp')]
	for shp in shp_list:
		for labTup in labels[:]:
			if labTup[0] in shp:
				clas = labTup[1]
		AddClassID(shp, clas)
	MergeSHPfiles(shp_list, mergedShape)
else:
	print("--> File already exists. Continuing...")

# (2) BUILD THE TWO RASTER-FILES
print("Build output rasterfiles")
# (2-1) LOAD THE FILES INTO GDAL
points = ogr.Open(mergedShape)
image = gdal.Open(mosaic_in)
# (2-2) GENERATE THE TWO RASTER FILES, GET PROPERTIES FOR THEM FIRST
nr_samples = GetFeatureCount(points)
nr_bands = GetNumberOfBands(image)
outDrv = gdal.GetDriverByName('ENVI')
spectra = outDrv.Create(out_spec, nr_samples, 1, nr_bands, GDT_UInt16)
labels = outDrv.Create(out_label, nr_samples, 1, 1, GDT_Byte)
# (2-3) LOOP OVER THE POINT-FEATURES, EXTRACT VALUES, WRITE TO LISTS
print("Extract Values")
lyr = points.GetLayer()
feat = lyr.GetNextFeature()
# Create the coordinate transformation
pol_srs = lyr.GetSpatialRef()
ras_srs = image.GetProjection()
target_SR = osr.SpatialReference()
target_SR.ImportFromWkt(ras_srs)
transform = osr.CoordinateTransformation(pol_srs, target_SR)
# Create output-lists, catch first feature
label_vals = []
image_vals = []
while feat:
# Get the label-value
	labelVal = feat.GetField("Class")
	label_vals.append(labelVal)
# Get the image-values
	imgVal = GetProfile(feat, transform, image, nr_bands)
	image_vals.append(imgVal)
# Switch to next feature
	feat = lyr.GetNextFeature()
lyr.ResetReading()
# Re-format values into row-like format, convert to np-array
vals_np = np.transpose(np.array(image_vals))
labs_np = np.transpose(np.array(label_vals))

# (2-4) WRITE VALUES TO OUTPUT-FILES
print("Write Output")
# Write output band-by-band
print("--> Image-Values")
for band in range(nr_bands):
# subset np-array by item --> corresponds to one band
	vals_sub = vals_np[band]
	vals_out = np.expand_dims(vals_sub, axis = 0)
	spectra.GetRasterBand((band+1)).WriteArray(vals_out, 0, 0)
print("--> Labels")
labs_out = np.expand_dims(labs_np, axis = 0)
labels.GetRasterBand(1).WriteArray(labs_out, 0, 0)

# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")