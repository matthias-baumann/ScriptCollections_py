# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import gdal
import ogr, osr
from gdalconst import *
import struct
import csv
import baumiTools as bt
from joblib import Parallel, delayed
from tqdm import tqdm
import os
# ####################################### SET TIME-COUNT ###################################################### #
if __name__ == '__main__':
	starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
	print("--------------------------------------------------------")
	print("Starting process, time:" +  starttime)
	print("")
# ####################################### FOLDER PATHS AND BASIC VARIABLES FOR PROCESSING ##################### #
	rootFolder = "L:/_PROJECTS/_Primary_Forests_and_Droughts/"
	#points_PF = rootFolder + "Analysis/01_Points_PrimaryForests/01_Sample_Min2.shp"
	points_control = rootFolder + "Analysis/02_Points_OtherForests/02_OtherForest_100000p_EuropeLandCover.shp"
	#out_PF = rootFolder + "Analysis/03_PointExtraction/01_PF-sample_2021-03-22.csv"
	out_control = rootFolder + "Analysis/03_PointExtraction/02_Control-sample_2021-03-22.csv"
	vitality = rootFolder + "Data_RS_vitality_indices/"
	spei_ras = rootFolder + "Data_drought_indices/spi-spei/eobs21e_spei12_19502019_200001201912.tif"
	spi_ras = rootFolder + "Data_drought_indices/spi-spei/eobs21e_spi12_19502019_200001201912.tif"
	access = rootFolder + "Data_covariates/1.1.Accessibility250.tif"
	gdd = rootFolder + "Data_covariates/2.1.GDD5.tif"
	rugg = rootFolder + "Data_covariates/4.4.ruggedness250.tif"
	solar = rootFolder + "Data_covariates/4.5.SolarRad.tif"
	nPackages = 50
	nr_cores = 51
# ####################################### PROCESSING ########################################################## #
# (1) Build job list
	jobList = []
	# Get the number of total features in the shapefile
	ps = ogr.Open(points_control)
	psLYR = ps.GetLayer()
	nFeat = psLYR.GetFeatureCount()
	# Create a list of UIDs and subdivide the into smaller chunks
	featIDs = list(range(1, nFeat+1, 1))
	packageSize = int(nFeat / nPackages)
	IDlist = [featIDs[i * packageSize:(i + 1) * packageSize] for i in range((len(featIDs) + packageSize - 1) // packageSize )]
	# Now build the jobs and append to job list
	for chunk in IDlist:
		job = {'ids': chunk,
               'point_path': points_control,
               'vital': vitality,
               'spei': spei_ras,
               'spi': spi_ras,
               'acc': access,
		       'gdd': gdd,
		       'rugg': rugg,
		       'solar': solar}
		jobList.append(job)
# (2) Build Worker_Function
	def WorkFunc(job):
		pts = bt.baumiVT.CopyToMem(job['point_path'])
		pts_lyr = pts.GetLayer()
		idSubs = job['ids']
		pts_lyr.SetAttributeFilter("ID IN {}".format(tuple(idSubs)))
		# Open the datasets (that are not the vitality indices)
		spei = gdal.Open(job['spei'], GA_ReadOnly)
		spi = gdal.Open(job['spi'], GA_ReadOnly)
		acc = gdal.Open(job['acc'], GA_ReadOnly)
		gdd = gdal.Open(job['gdd'], GA_ReadOnly)
		rugg = gdal.Open(job['rugg'], GA_ReadOnly)
		solar = gdal.Open(job['solar'], GA_ReadOnly)

		def ExtractPoint(geom, raster, band):
			gdal.UseExceptions()
			try:
				rb = raster.GetRasterBand(band)
				pr = raster.GetProjection()
				gt = raster.GetGeoTransform()
				rasdType = bt.baumiRT.GetDataTypeHexaDec(rb.DataType)
				# Create coordinate transformation for point
				source_SR = geom.GetSpatialReference()
				source_SR.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
				target_SR = osr.SpatialReference()
				target_SR.ImportFromWkt(pr)
				target_SR.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
				cT = osr.CoordinateTransformation(source_SR, target_SR)
				# Now extact the point from the rast
				geom_cl = geom.Clone()
				geom_cl.Transform(cT)
				mx, my = geom_cl.GetX(), geom_cl.GetY()
				# Extract raster value
				px = int((mx - gt[0]) / gt[1])
				py = int((my - gt[3]) / gt[5])
				structVar = rb.ReadRaster(px, py, 1, 1)
				Val = struct.unpack(rasdType, structVar)[0]
			except:
				Val = 'NA'
			return Val

		# now loop over the features and extract the point at the location of the raster
		outList = []
		feat = pts_lyr.GetNextFeature()
		while feat:
		# Retrieve the infos from the attribute table
			id = feat.GetField("ID")
			#print(id)
			geom = feat.GetGeometryRef()
			values = [id]
		# Get the time-invariant variables
			values.append(ExtractPoint(geom.Clone(), acc, 1))
			values.append(ExtractPoint(geom.Clone(), gdd, 1))
			values.append(ExtractPoint(geom.Clone(), rugg, 1))
			values.append(ExtractPoint(geom.Clone(), solar, 1))
		# get the values of the vitality values
			vit_list = [job['vital'] + ras for ras in os.listdir(job['vital']) if ras.endswith('.tif')]
			for ras in vit_list:
				ds = gdal.Open(ras, GA_ReadOnly)
				values.append(ExtractPoint(geom.Clone(), ds, 1))
		# Get SPI and SPEI
			# 2017
			values.append(ExtractPoint(geom.Clone(), spei, 18))
			values.append(ExtractPoint(geom.Clone(), spi, 18))
			# 2018
			values.append(ExtractPoint(geom.Clone(), spei, 19))
			values.append(ExtractPoint(geom.Clone(), spi, 19))
			# 2019
			values.append(ExtractPoint(geom.Clone(), spei, 20))
			values.append(ExtractPoint(geom.Clone(), spi, 20))
			# Take next feature
			outList.append(values)
			feat = pts_lyr.GetNextFeature()
		return outList
# (3) Execute the Worker_Funtion parallel
	job_results = Parallel(n_jobs=nr_cores)(delayed(WorkFunc)(i) for i in tqdm(jobList))
	#for job in jobList:
	#	list = WorkFunc(job)
# (4) Merge the different packages back together into one dataset, instantiate colnames first
	print("Merge Outputs")
	outDS = [["UniqueID", "Acc", "gdd", "rugg", "solar",
	          "ndmi_2018-06", "ndmi_2018-07", "ndmi_2018-08", "ndmi_2018-09", "ndmi_2019-06", "ndmi_2019-07", "ndmi_2019-08", "ndmi_2019-09",
	          "ndvi_2018-06", "ndvi_2018-07", "ndvi_2018-08", "ndvi_2018-09", "ndvi_2019-06", "ndvi_2019-07", "ndvi_2019-08", "ndvi_2019-09",
	          "spei_2017", "spi_2017", "spei_2018", "spi_2018", "spei_2019", "spi_2019"]]
	# Now extract the information from all the evaluations
    # 1st loop --> the different chunks
	for result in job_results:
		# 2nd loop --> all outputs in each chunk
		for out in result:
			outDS.append(out)
# (5) Write all outputs to disc
	print("Write output")
	with open(out_control, "w") as theFile:
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