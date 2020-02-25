# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import ogr, gdal, osr
import baumiTools as bt
from tqdm import tqdm
from joblib import Parallel, delayed
import numpy as np
if __name__ == '__main__':
	starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
	print("--------------------------------------------------------")
	print("Starting process, time:" +  starttime)
	print("")
# ####################################### FOLDER PATHS AND BASIC VARIABLES FOR PROCESSING ##################### #
	#rootFolder = "D:/_RESEARCH/Publications/Publications-in-preparation/butsic-etal_cannabis/"
	rootFolder = "D:/baumamat/butsic-etal_cannabis/"
	outputFile = rootFolder + "Summary_SiskiyouCounty_20190814.csv"
	filesFolder = rootFolder + "Data_SiskiyouCounty/"
	epsg_to = 3310
	uid_field = "APN"
	nPackages = 500
	nr_cores = 50
# ####################################### PROCESSING ########################################################## #
# (1) Build job list
	jobList = []
# Get the number of total features in the shapefile
	shp = ogr.Open(filesFolder + "parcels_inGrid.shp")
	shpLYR = shp.GetLayer()
	nFeat = shpLYR.GetFeatureCount()
# Create a list of UIDs and subdivide the into smaller chunks
	featIDs = list(range(1, nFeat+1, 1))
	packageSize = int(nFeat / nPackages)
	IDlist = [featIDs[i * packageSize:(i + 1) * packageSize] for i in range((len(featIDs) + packageSize - 1) // packageSize )]
# Now build the jobs and append to job list
	for chunk in IDlist:
		job = {'ids': chunk,
               'shp_path': filesFolder + "parcels_inGrid.shp",
               'epsg': epsg_to,
               'files': filesFolder}
		jobList.append(job)
# (2) Build Worker_Function
	def SumFunc(job):
# ####################################### FUNCTIONS ########################################################### #
		def calcCannabisArea(geom, file):
			lyr = file.GetLayer()
			# Build coordinate transformation
			fromSR = lyr.GetSpatialRef()
			toSR = geom.GetSpatialReference()
			tr = osr.CoordinateTransformation(fromSR, toSR)
			# make a sum area
			area_sum = 0
			lyr_feat = lyr.GetNextFeature()
			while lyr_feat:
			# Load the geometry, project to parcel-CS
				featGEOM = lyr_feat.GetGeometryRef()
				featGEOM.Transform(tr)
				featGEOM_b = featGEOM.Buffer(0)
			# Calculate the intersection, then the area
				intersection = geom.Intersection(featGEOM_b)
				area_m2 = intersection.GetArea()
				area_sum = area_sum + area_m2
			# Next feature
				lyr_feat = lyr.GetNextFeature()
			lyr.ResetReading()
			return round(area_sum, 3)
		def calcCityDist(geom, file):
			lyr = file.GetLayer()
			# Convert geometry to the layer file
			#fromSR = geom.GetSpatialReference()
			#toSR = lyr.GetSpatialRef()
			#tr = osr.CoordinateTransformation(fromSR, toSR)
			#geom.Transform(tr)
			# Set Intersect-Flag, and buffer step size
			flag = 0
			buffer = 0
			stepSize = 50
			while flag == 0:
				geom_bf = geom.Buffer(buffer)
			# Check if it a spatal filter returns at least one element in lyr
				lyr.SetSpatialFilter(geom_bf)
				city_yn = lyr.GetFeatureCount()
				if city_yn > 0:
					flag = 1
				else:
					flag = flag
					buffer = buffer + stepSize
			return buffer / 1000
		def calcMaxNLCD(geom, file):
			# Make a coordinate transformation of the geom-srs to the raster-srs
			pol_srs = geom.GetSpatialReference()
			ras_srs = file.GetProjection()
			target_SR = osr.SpatialReference()
			target_SR.ImportFromWkt(ras_srs)
			srs_trans = osr.CoordinateTransformation(pol_srs, target_SR)
			geom.Transform(srs_trans)
			# Create a memory shp/lyr to rasterize in
			geom_shp = ogr.GetDriverByName('Memory').CreateDataSource('')
			geom_lyr = geom_shp.CreateLayer('geom_shp', srs=geom.GetSpatialReference())
			geom_feat = ogr.Feature(geom_lyr.GetLayerDefn())
			geom_feat.SetGeometryDirectly(ogr.Geometry(wkt=str(geom)))
			geom_lyr.CreateFeature(geom_feat)
			# Rasterize the layer, open in numpy
			# bt.baumiVT.CopySHPDisk(geom_shp, "D:/baumamat/Warfare/_Variables/Forest/_tryout.shp")
			x_min, x_max, y_min, y_max = geom.GetEnvelope()
			x_res = int((x_max - x_min) / 30)
			y_res = int((y_max - y_min) / 30)
			if x_res > 0 and y_res > 0:
				gt = file.GetGeoTransform()
				pr = file.GetProjection()
				x_res = int((abs(x_max - x_min)) / gt[1])
				y_res = int((abs(y_max - y_min)) / gt[1])
				new_gt = (x_min, gt[1], 0, y_max, 0, -gt[1])
				lyr_ras = gdal.GetDriverByName('MEM').Create('', x_res, y_res, 1, gdal.GDT_Byte)
				lyr_ras.GetRasterBand(1).SetNoDataValue(0)
				lyr_ras.SetProjection(pr)
				lyr_ras.SetGeoTransform(new_gt)
				gdal.RasterizeLayer(lyr_ras, [1], geom_lyr, burn_values=[1])
				geom_np = np.array(lyr_ras.GetRasterBand(1).ReadAsArray())
				# Now load the raster into the array --> only take the area that is 1:1 the geom-layer (see Garrard p.195)
				inv_gt = gdal.InvGeoTransform(gt)
				offsets_ul = gdal.ApplyGeoTransform(inv_gt, x_min, y_max)
				off_ul_x, off_ul_y = map(int, offsets_ul)
				raster_np = np.array(file.GetRasterBand(1).ReadAsArray(off_ul_x, off_ul_y, x_res, y_res))
				raster_np_mask = np.where(geom_np == 1, raster_np, 0)
				try:
					whichMax = (np.bincount(raster_np_mask[raster_np_mask > 0]).argmax())
				except:
					whichMax = 0
			else:
				whichMax = 0
			return whichMax
		def calcRoach(geom, file):
			lyr = file.GetLayer()
			# Build coordinate transformation
			fromSR = lyr.GetSpatialRef()
			toSR = geom.GetSpatialReference()
			tr = osr.CoordinateTransformation(fromSR, toSR)
			# make a sum area
			area_sum = 0
			lyr_feat = lyr.GetNextFeature()
			while lyr_feat:
			# Load the geometry, project to parcel-CS
				featGEOM = lyr_feat.GetGeometryRef()
				featGEOM.Transform(tr)
				featGEOM_b = featGEOM.Buffer(0)
			# Calculate the intersection, then the area
				intersection = geom.Intersection(featGEOM_b)
				area_m2 = intersection.GetArea()
				area_sum = area_sum + area_m2
			# Next feature
				lyr_feat = lyr.GetNextFeature()
			# Claculate percentage of roach habitat in parcel
			perc = area_sum / geom.GetArea()
			lyr.ResetReading()
			return round(perc, 3)
		def calcTPImax(geom, file):
			lyr = file.GetLayer()
			# Convert geometry to lyr CS
			fromSR = geom.GetSpatialReference()
			toSR = lyr.GetSpatialRef()
			tr = osr.CoordinateTransformation(fromSR, toSR)
			geom.Transform(tr)
			# Look through those that intersect with geometry
			lyr.SetSpatialFilter(geom)
			feat = lyr.GetNextFeature()
			TPIs = []
			while feat:
				TPIs.append(feat.GetField("TPIS"))
				feat = lyr.GetNextFeature()
			# Calculate the maximum of the TPIs
			lyr.ResetReading()
			return max(TPIs)
		def calcRoadDist(geom, file):
			lyr = file.GetLayer()
			# Convert geometry to the layer file
			# fromSR = geom.GetSpatialReference()
			# toSR = lyr.GetSpatialRef()
			# tr = osr.CoordinateTransformation(fromSR, toSR)
			# geom.Transform(tr)
			# Set Intersect-Flag, and buffer step size
			flag = 0
			buffer = 0
			stepSize = 1
			while flag == 0:
				geom_bf = geom.Buffer(buffer)
				# Check if it a spatal filter returns at least one element in lyr
				lyr.SetSpatialFilter(geom_bf)
				city_yn = lyr.GetFeatureCount()
				if city_yn > 0:
					flag = 1
				else:
					flag = flag
					buffer = buffer + stepSize
			return buffer / 1000
		def calcDrainage(geom, file):
			lyr = file.GetLayer()
			# Convert geometry to lyr CS
			fromSR = geom.GetSpatialReference()
			toSR = lyr.GetSpatialRef()
			tr = osr.CoordinateTransformation(fromSR, toSR)
			# Set initial values
			drainName = "None"
			drainPerc = 0
			# Run through the soils the geometry intersects with
			geom.Transform(tr)
			lyr.SetSpatialFilter(geom)
			feat = lyr.GetNextFeature()
			while feat:
				geom_feat = feat.GetGeometryRef()
				areaProp = geom_feat.GetArea() / geom.GetArea()
				if areaProp > drainPerc:
					drainPerc = areaProp
					drainName = feat.GetField("drainage")
				else:
					drainPerc = drainPerc
					drainName = drainName
				feat = lyr.GetNextFeature()
			lyr.ResetReading()
			return drainName
		def calcPA(geom, file):
			lyr = file.GetLayer()
			# Convert geometry to lyr CS
			fromSR = geom.GetSpatialReference()
			toSR = lyr.GetSpatialRef()
			tr = osr.CoordinateTransformation(fromSR, toSR)
			geom.Transform(tr)
			centroid = geom.Centroid()
			# Check whether centroid intersects with any geometry
			lyr.SetSpatialFilter(centroid)
			InOut = lyr.GetFeatureCount()
			# If inside, the vlaue for the binary code is '1', and the distance to PA is '0'
			if InOut > 0:
				feat = lyr.GetNextFeature()
				gapSTS = feat.GetField("GAP_STS")
				# Calculate binary
				out = [1, 0, gapSTS]
				lyr.ResetReading()
			else:
				flag = 0
				buffer = 0
				stepSize = 50
				while flag == 0:
					geom_bf = geom.Buffer(buffer)
					# Check if it a spatal filter returns at least one element in lyr
					lyr.SetSpatialFilter(geom_bf)
					PA_yn = lyr.GetFeatureCount()
					if PA_yn > 0:
						flag = 1
					else:
						flag = flag
						buffer = buffer + stepSize
				out = [0, buffer / 1000, 'NA']
			return out
		def calcCannanbisArea_dist(geom, file, distance):
			lyr = file.GetLayer()
			# Build coordinate transformation
			fromSR = lyr.GetSpatialRef()
			toSR = geom.GetSpatialReference()
			tr = osr.CoordinateTransformation(fromSR, toSR)
			# calculate the buffer around the geometry
			geom_buff = geom.Buffer(distance)
			geomBuffOnly = geom_buff.Difference(geom)
			#bt.baumiVT.SaveGEOMtoFile(geomBuffOnly, rootFolder + "test.shp")
			#exit(0)
			# make a sum area
			area_sum = 0
			lyr_feat = lyr.GetNextFeature()
			while lyr_feat:
			# Load the geometry, project to parcel-CS
				featGEOM = lyr_feat.GetGeometryRef()
				featGEOM.Transform(tr)
				featGEOM_b = featGEOM.Buffer(0)
			# Calculate the intersection, then the area
				intersection = geomBuffOnly.Intersection(featGEOM_b)
				area_m2 = intersection.GetArea()
				area_sum = area_sum + area_m2
			# Next feature
				lyr_feat = lyr.GetNextFeature()
			lyr.ResetReading()
			return round(area_sum, 3)
# ####################################### LOOP THROUGH FEATURES ############################################### #
		packageList = []
	# (1) LOAD THE DIFFERENT FILES INTO MEMORY
		GH2012 = bt.baumiVT.CopyToMem(job['files'] + "green2012.shp")
		GH2014 = bt.baumiVT.CopyToMem(job['files'] + "green2014.shp")
		GH2016 = bt.baumiVT.CopyToMem(job['files'] + "green2016.shp")
		OD2012 = bt.baumiVT.CopyToMem(job['files'] + "outdoor2012.shp")
		OD2014 = bt.baumiVT.CopyToMem(job['files'] + "outdoor2014.shp")
		OD2016 = bt.baumiVT.CopyToMem(job['files'] + "outdoor2016.shp")
		cities = bt.baumiVT.CopyToMem(job['files'] + "cities_proj.shp")
		nlcd = bt.baumiRT.OpenRasterToMemory(job['files'] + "nlcd_TIFF.tif")
		roach = bt.baumiVT.CopyToMem(job['files'] + "roach.shp")
		TPI = bt.baumiVT.CopyToMem(job['files'] + "TPIS.shp")
		roads = bt.baumiVT.CopyToMem(job['files'] + "roads_proj.shp")
		named_roads = bt.baumiVT.CopyToMem(job['files'] + "named_roads_proj.shp")
		soils = bt.baumiVT.CopyToMem(job['files'] + "soil.shp")
		PAs = bt.baumiVT.CopyToMem(job['files'] + "protectedarea.shp")
		# (3) GET PARCELS, SUBSET BY THE SUBPACKAGE, BUILD COORDINATE TRANSFORMATION, START LOOPING THROUGH THE LYR
		shpMem = bt.baumiVT.CopyToMem(job['shp_path'])
		lyr = shpMem.GetLayer()
		idSubs = job['ids']
		lyr.SetAttributeFilter("UID IN {}".format(tuple(idSubs)))
		parcels_SR = lyr.GetSpatialRef()
		target_SR = osr.SpatialReference()
		target_SR.ImportFromEPSG(epsg_to)
		trans = osr.CoordinateTransformation(parcels_SR, target_SR)
		feat = lyr.GetNextFeature()
		while feat:
		#for feat in tqdm(LYR):
			geom = feat.GetGeometryRef()
			geom_cl = geom.Clone()
			geom_cl.Transform(trans)
		# Instantiate output-list, get necessary fields, calculate area
			data = [feat.GetField("APN"), round(geom_cl.GetArea(), 3)]
		# Calculate the area of cannabis in greenhouse per parcel
			data.append(calcCannabisArea(geom_cl.Clone(), GH2012))
			data.append(calcCannabisArea(geom_cl.Clone(), GH2014))
			data.append(calcCannabisArea(geom_cl.Clone(), GH2016))
		# Calculate the area of cannabis in outdoor grows
			data.append(calcCannabisArea(geom_cl.Clone(), OD2012))
			data.append(calcCannabisArea(geom_cl.Clone(), OD2014))
			data.append(calcCannabisArea(geom_cl.Clone(), OD2016))
		# Calculate the distance to nearest city
			data.append(calcCityDist(geom_cl.Clone(), cities))
		# Calculate maximum NLCD
			data.append(calcMaxNLCD(geom_cl.Clone(), nlcd))
		# Calculate roach percent
			data.append(calcRoach(geom_cl.Clone(), roach))
		# Calculate TPIS max
			data.append(calcTPImax(geom_cl.Clone(), TPI))
		# Calculate road distances
			data.append(calcRoadDist(geom_cl.Clone(), roads))
			data.append(calcRoadDist(geom_cl.Clone(), named_roads))
		# Calculate soil drainage
			data.append(calcDrainage(geom_cl.Clone(), soils))
		# calculate protected area
			data.extend(calcPA(geom_cl.Clone(), PAs))
		# Calculate the area of cannabis in greenhouse per parcel in distance of 100m
			data.append(calcCannanbisArea_dist(geom_cl.Clone(), GH2012, 100))
			data.append(calcCannanbisArea_dist(geom_cl.Clone(), GH2014, 100))
			data.append(calcCannanbisArea_dist(geom_cl.Clone(), GH2016, 100))
		# Calculate the area of cannabis in outdoor grows per parcel in distance of 100m
			data.append(calcCannanbisArea_dist(geom_cl.Clone(), OD2012, 100))
			data.append(calcCannanbisArea_dist(geom_cl.Clone(), OD2014, 100))
			data.append(calcCannanbisArea_dist(geom_cl.Clone(), OD2016, 100))
		# Calculate the area of cannabis in greenhouse per parcel in distance of 500m
			data.append(calcCannanbisArea_dist(geom_cl.Clone(), GH2012, 500))
			data.append(calcCannanbisArea_dist(geom_cl.Clone(), GH2014, 500))
			data.append(calcCannanbisArea_dist(geom_cl.Clone(), GH2016, 500))
		# Calculate the area of cannabis in outdoor grows per parcel in distance of 500m
			data.append(calcCannanbisArea_dist(geom_cl.Clone(), OD2012, 500))
			data.append(calcCannanbisArea_dist(geom_cl.Clone(), OD2014, 500))
			data.append(calcCannanbisArea_dist(geom_cl.Clone(), OD2016, 500))
	# Append to outlist, take next feature
			packageList.append(data)
			feat = lyr.GetNextFeature()
		return packageList
# (3) Execute worker function
	job_results = Parallel(n_jobs=nr_cores)(delayed(SumFunc)(i) for i in tqdm(jobList))
# Write output-file
print("Build output")
# (1) Extract the results, write to output list
outList = [["APN", "ParcelArea_km", "GH2012_m2", "GH2014_m2", "GH2016_m2", "OD2012_m2", "OD2014_m2", "OD2016_m2",
			"CityDist_km", "NLCD_main", "Roach_perc", "Max_TPIS", "RoadDist_km", "NamedRoadDist_km", "Drain_main",
			"PA_yn", "PAdist_km", "GAP_STS", "GH100m_2012_m2", "GH100m_2014_m2", "GH100m_2016_m2", "GH500m_2012_m2",
			"GH500m_2014_m2", "GH500m_2016_m2", "OD100m_2012_m2", "OD100m_2014_m2", "OD100m_2016_m2", "OD500m_2012_m2",
			"OD500m_2014_m2", "OD500m_2016_m2"]]
for result in tqdm(job_results):
	for line in result:
		outList.append(line)
# Write to file
bt.baumiFM.WriteListToCSV(outputFile, outList, ",")
# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")