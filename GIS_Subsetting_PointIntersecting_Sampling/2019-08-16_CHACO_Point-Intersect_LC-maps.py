# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import gdal
import ogr, osr
from gdalconst import *
import struct
import csv
import baumiTools as bt
import baumiTools as bt
from joblib import Parallel, delayed
from tqdm import tqdm
# ####################################### SET TIME-COUNT ###################################################### #
if __name__ == '__main__':
	starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
	print("--------------------------------------------------------")
	print("Starting process, time:" +  starttime)
	print("")
# ####################################### FOLDER PATHS AND BASIC VARIABLES FOR PROCESSING ##################### #
	rootFolder = "E:/Baumann/_ANALYSES/AnnualLandCoverChange_CHACO/"
	#points = rootFolder + "06_MapValidation/Result_Intercomparison/RandomPoints_Guyra.shp"
	points = rootFolder + "06_MapValidation/Run05ForestLoss_1985-2018_annual_randomSample_50ppC.shp"
	out_file = rootFolder + "06_MapValidation/Result_Intercomparison/Run05ForestLoss_1985-2018_annual_20191029.csv"
	hansen = "Z:/Warfare/_Variables/Forest/LossYear.vrt"
	#guyra = rootFolder + "06_MapValidation/Result_Intercomparison/GuyraPlots_All_raster.tif"
	#run02 = rootFolder + "04_Map_Products/Run02/Run02_ForestLoss_1985-2018_annual_GCS-WGS84_CHACO-plus.tif"
	#run04 = rootFolder + "04_Map_Products/Run04/Run04_ForestLoss_1985-2018_annual_GCS-WGS84_CHACO-plus.tif"
	run05 = rootFolder + "04_Map_Products/Run05/ForestLoss_1985-2019.tif"
	nPackages = 30
	nr_cores = 50
# ####################################### PROCESSING ########################################################## #
# (1) Build job list
	jobList = []
	# Get the number of total features in the shapefile
	ps = ogr.Open(points)
	psLYR = ps.GetLayer()
	nFeat = psLYR.GetFeatureCount()
	# Create a list of UIDs and subdivide the into smaller chunks
	featIDs = list(range(1, nFeat+1, 1))
	packageSize = int(nFeat / nPackages)
	IDlist = [featIDs[i * packageSize:(i + 1) * packageSize] for i in range((len(featIDs) + packageSize - 1) // packageSize )]
	# Now build the jobs and append to job list
	for chunk in IDlist:
		job = {'ids': chunk,
               'point_path': points,
               #'hansenPath': hansen,
               #'guyraPath': guyra,
               #'run02': run02,
               #'run04': run04,
		       'run05': run05}
		jobList.append(job)
# (2) Build Worker_Function
	def WorkFunc(job):
		pts = bt.baumiVT.CopyToMem(job['point_path'])
		pts_lyr = pts.GetLayer()
		idSubs = job['ids']
		pts_lyr.SetAttributeFilter("ID IN {}".format(tuple(idSubs)))
		# Open Hansen
		#hansen = gdal.Open(job['hansenPath'], GA_ReadOnly)
		# Open guyra
		#guyra = gdal.Open(job['guyraPath'], GA_ReadOnly)
		# Open classifications
		#r2 = gdal.Open(job['run02'], GA_ReadOnly)
		#r4 = gdal.Open(job['run04'], GA_ReadOnly)
		r5 = gdal.Open(job['run05'], GA_ReadOnly)


		def ExtractPoint(geom, raster):
			rb = raster.GetRasterBand(1)
			pr = raster.GetProjection()
			gt = raster.GetGeoTransform()
			rasdType = bt.baumiRT.GetDataTypeHexaDec(rb.DataType)
			# Create coordinate transformation for point
			source_SR = geom.GetSpatialReference()
			target_SR = osr.SpatialReference()
			target_SR.ImportFromWkt(pr)
			cT = osr.CoordinateTransformation(source_SR, target_SR)
			# Now extact the point from the rast
			geom_cl = geom.Clone()
			geom.Transform(cT)
			mx, my = geom_cl.GetX(), geom_cl.GetY()
			# Extract raster value
			px = int((mx - gt[0]) / gt[1])
			py = int((my - gt[3]) / gt[5])
			structVar = rb.ReadRaster(px, py, 1, 1)
			Val = struct.unpack(rasdType, structVar)[0]
			return Val

		# now loop over the features and extract the point at the location of the raster
		outList = []
		feat = pts_lyr.GetNextFeature()
		while feat:
		# Retrieve the infos from the attribute table
			id = feat.GetField("ID")
			geom = feat.GetGeometryRef()
			#val_hansen = ExtractPoint(geom, hansen) + 2000
			#val_guyra = ExtractPoint(geom, guyra)
			#val_r2 = ExtractPoint(geom, r2)
			#val_r4 = ExtractPoint(geom, r4)
			val_r5 = ExtractPoint(geom, r5)
			#values = [id, val_hansen, val_guyra, val_r2, val_r4, val_r5]
			values = [id, val_r5]
			# Take next feature
			outList.append(values)
			feat = pts_lyr.GetNextFeature()
		return outList
# (3) Execute the Worker_Funtion parallel
	job_results = Parallel(n_jobs=nr_cores)(delayed(WorkFunc)(i) for i in tqdm(jobList))
	#for job in jobList:
    #   list = SumFunc(job)
# (4) Merge the different packages back together into one dataset, instantiate colnames first
	print("Merge Outputs")
	#outDS = [["UniqueID", "Hansen", "guyra", "Run_02", "Run_04", "Run_05"]]
	outDS = [["UniqueID", "Run_05"]]
	# Now extract the information from all the evaluations
    # 1st loop --> the different chunks
	for result in job_results:
		# 2nd loop --> all outputs in each chunk
		for out in result:
			outDS.append(out)
# (5) Write all outputs to disc
	print("Write output")
	with open(out_file, "w") as theFile:
		csv.register_dialect("custom", delimiter = ";", skipinitialspace = True, lineterminator = '\n')
		writer = csv.writer(theFile, dialect = "custom")
		for element in outDS:
			writer.writerow(element)
# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
	print("")
	endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
	print("--------------------------------------------------------")
	print("--------------------------------------------------------")
	print("start: " + starttime)
	print("end: " + endtime)
	print("")