# ####################################### IMPORT MODULES, START EARTH-ENGINE ################################## #
import os
import re
import baumiTools as bt
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import gdal, ogr, osr, json
import time
import warnings
import ee
import numpy as np

# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " + starttime)
print("")
# ####################################### FILES AND FOLDER-PATHS ############################################## #
workFolder = "D:/OneDrive - Conservation Biogeography Lab/_RESEARCH/Projects_Active/_Vanishing_Treasures/"
studyArea = bt.baumiVT.CopyToMem(workFolder + "Variables/KGZ_TJK_150kmBuffer_WGS84.shp")
output_folder = workFolder + "Variables/"
tilevar = "Id"
maxTasks = 2

# ####################################### FUNCTIONS ########################################################### #
def Calculate_Landsat_Seasonal_Mean(year, startMonth, endMonth, roi, mask_clouds=True, mask_water=False,
                                      mask_snow=False, mask_fill=True, harmonize_l8=True):

	# In case we switch to the surrounding year, we have to increase the year counter for the end date, that is why we need to specify the Startyear and endYear
	yearStart = year
	yearEnd = year
	# Convert the information on year, startMonth, endMonth to a date for the filter --> define lastday of endMonth based on how many days are in that month
	if endMonth in [4, 6, 9, 11]:
		lastDay = 30
	if endMonth in [1, 3, 5, 7, 8, 10, 12]:
		lastDay = 31
	if endMonth == 2:
		lastDay = 28
	start = ee.Date.fromYMD(yearStart, startMonth, 1)
	end = ee.Date.fromYMD(yearEnd, endMonth, lastDay)
	# band names in input and output collections
	bands = ['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'B6', 'pixel_qa']
	band_names = ['B', 'G', 'R', 'NIR', 'SWIR1', 'SWIR2', 'T', 'pixel_qa']
	l8bands = ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B1', 'B10', 'B11', 'pixel_qa']
	l8band_names = ['B', 'G', 'R', 'NIR', 'SWIR1', 'SWIR2', 'UB', 'T1', 'T2', 'pixel_qa']
	# qa bits
	cloudbit = ee.Number(ee.Algorithms.If(mask_clouds, 40, 0))
	waterbit = ee.Number(ee.Algorithms.If(mask_water, 4, 0))
	snowbit = ee.Number(ee.Algorithms.If(mask_snow, 16, 0))
	fillbit = ee.Number(ee.Algorithms.If(mask_fill, 1, 0))
	bits = cloudbit.add(waterbit).add(snowbit).add(fillbit)
	## helper functions
	# function to apply masks based on pixel qa band
	def apply_masks(img):
		qa = img.select('pixel_qa')
		mask = qa.bitwiseAnd(bits).eq(0)
		return img.updateMask(mask)
	# function to harmonize l8 surface reflectance with coefficients from Roy et al. 2016
	def l8_harmonize(l8img):
		b = ee.Image(0.0183).add(ee.Image(0.8850).multiply(l8img.select('B'))).int16()
		g = ee.Image(0.0123).add(ee.Image(0.9317).multiply(l8img.select('G'))).int16()
		r = ee.Image(0.0123).add(ee.Image(0.9372).multiply(l8img.select('R'))).int16()
		nir = ee.Image(0.0448).add(ee.Image(0.8339).multiply(l8img.select('NIR'))).int16()
		swir1 = ee.Image(0.0306).add(ee.Image(0.8639).multiply(l8img.select('SWIR1'))).int16()
		swir2 = ee.Image(0.0116).add(ee.Image(0.9165).multiply(l8img.select('SWIR2'))).int16()

		out = ee.Image(b.addBands(g).addBands(r).addBands(nir).addBands(swir1).addBands(swir2).addBands(
			l8img.select(['UB', 'T1', 'T2', 'pixel_qa'])).copyProperties(l8img, l8img.propertyNames())).rename(
			l8band_names)
		return out
	# function to remove double counts from path overlap areas
	def remove_double_counts(collection):
		def add_nn(image):
			start = ee.Date.fromYMD(image.date().get('year'), image.date().get('month'),
			                        image.date().get('day')).update(hour=0, minute=0, second=0)
			end = ee.Date.fromYMD(image.date().get('year'), image.date().get('month'), image.date().get('day')).update(
				hour=23, minute=59, second=59)
			overlapping = collection.filterDate(start, end).filterBounds(image.geometry())
			nn = overlapping.filterMetadata('WRS_ROW', 'equals', ee.Number(image.get('WRS_ROW')).subtract(1)).size()
			return image.set('nn', nn)

		collection_nn = collection.map(add_nn)
		has_nn = collection_nn.filterMetadata('nn', 'greater_than', 0)
		has_no_nn = ee.ImageCollection(ee.Join.inverted().apply(collection, has_nn,
		                                                        ee.Filter.equals(leftField='LANDSAT_ID',
		                                                                         rightField='LANDSAT_ID')))

		def mask_overlap(image):
			start = ee.Date.fromYMD(image.date().get('year'), image.date().get('month'),
			                        image.date().get('day')).update(hour=0, minute=0, second=0)
			end = ee.Date.fromYMD(image.date().get('year'), image.date().get('month'), image.date().get('day')).update(
				hour=23, minute=59, second=59)
			overlapping = collection.filterDate(start, end).filterBounds(image.geometry())
			nn = ee.Image(
				overlapping.filterMetadata('WRS_ROW', 'equals', ee.Number(image.get('WRS_ROW')).subtract(1)).first())
			newmask = image.mask().where(nn.mask(), 0)
			return image.updateMask(newmask)

		has_nn_masked = ee.ImageCollection(has_nn.map(mask_overlap))
		out = ee.ImageCollection(has_nn_masked.merge(has_no_nn).copyProperties(collection))
		return out
	# Function to calculate a standard set of indices
	def landsat_indices(landsat, indices):
		# helper functions to add spectral indices to collections
		def add_NBR(image):
			nbr = image.normalizedDifference(['NIR', 'SWIR2']).rename('NBR')
			nbr = nbr.multiply(10000).int()
			return image.addBands(nbr)

		def add_NDMI(image):
			ndmi = image.normalizedDifference(['NIR', 'SWIR1']).rename('NDMI')
			ndmi = ndmi.multiply(10000).int()
			return image.addBands(ndmi)

		def add_NDVI(image):
			ndvi = image.normalizedDifference(['NIR', 'R']).rename('NDVI')
			ndvi = ndvi.multiply(10000).int()
			return image.addBands(ndvi)

		def add_EVI(image):
			evi = image.expression('2.5 * ((NIR - R) / (NIR + 6 * R - 7.5 * B + 1))',
			                       {'NIR': image.select('NIR'), 'R': image.select('R'), 'B': image.select('B')}).rename(
				'EVI')
			evi = evi.multiply(10000).int()
			return image.addBands(evi)

		def add_MSAVI(image):
			msavi = image.expression('(2 * NIR + 1 - sqrt(pow((2 * NIR + 1), 2) - 8 * (NIR - R)) ) / 2',
			                         {'NIR': image.select('NIR'), 'R': image.select('R')}).rename('MSAVI')
			msavi = msavi.multiply(10000).int()
			return image.addBands(msavi)

		def add_TC(image):
			img = image.select(['B', 'G', 'R', 'NIR', 'SWIR1', 'SWIR2'])
			# coefficients for Landsat surface reflectance (Crist 1985)
			brightness_c = ee.Image([0.3037, 0.2793, 0.4743, 0.5585, 0.5082, 0.1863])
			greenness_c = ee.Image([-0.2848, -0.2435, -0.5436, 0.7243, 0.0840, -0.1800])
			wetness_c = ee.Image([0.1509, 0.1973, 0.3279, 0.3406, -0.7112, -0.4572])
			brightness = img.multiply(brightness_c)
			greenness = img.multiply(greenness_c)
			wetness = img.multiply(wetness_c)
			brightness = brightness.reduce(ee.call('Reducer.sum')).int()
			greenness = greenness.reduce(ee.call('Reducer.sum')).int()
			wetness = wetness.reduce(ee.call('Reducer.sum'))
			wetness = wetness.multiply(-1).int()
			tasseled_cap = ee.Image(brightness).addBands(greenness).addBands(wetness).rename(['tcB', 'tcG', 'tcW'])
			return image.addBands(tasseled_cap)

		out = landsat.map(add_NBR).map(add_NDMI).map(add_EVI).map(add_MSAVI).map(add_NDVI).map(add_TC).select(indices)
		return out
	# Introduce a flag. This flag controls, that there are any images in the collection that build the image.
	# If there arent't any, the the season of interest will be extended by 3 months until there are images
	l4 = remove_double_counts(ee.ImageCollection('LANDSAT/LT04/C01/T1_SR').filterBounds(roi).select(bands, band_names).filter(ee.Filter.date(start, end)).map(apply_masks))
	l5 = remove_double_counts(ee.ImageCollection('LANDSAT/LT05/C01/T1_SR').filterBounds(roi).select(bands, band_names).filter(ee.Filter.date(start, end)).map(apply_masks))
	l7 = remove_double_counts(ee.ImageCollection('LANDSAT/LE07/C01/T1_SR').filterBounds(roi).select(bands, band_names).filter(ee.Filter.date(start, end)).map(apply_masks))
	l8 = remove_double_counts(ee.ImageCollection('LANDSAT/LC08/C01/T1_SR').filterBounds(roi).select(l8bands, l8band_names).filter(ee.Filter.date(start, end)).map(apply_masks))
	l8h = ee.ImageCollection(ee.Algorithms.If(harmonize_l8, l8.map(l8_harmonize), l8))
	# combine landsat collections
	landsat_data = ee.ImageCollection(l4.merge(l5).merge(l7).merge(l8h)).select(['B', 'G', 'R', 'NIR', 'SWIR1', 'SWIR2'])
	# Add the indices
	spectral_indices = landsat_indices(landsat_data, ["NDVI", "NDMI", "EVI",  "tcW", "tcB", "tcG"]) # "NBR""MSAVI",
	# Create the reducers
	mean = ee.Reducer.mean().unweighted()
	# Calculate the predictors
	predictors = spectral_indices.reduce(mean)
	return predictors

def Calculate_Mean_NDSI(year, startMonth, endMonth, roi):
	# Credits go to: https://github.com/khufkens/MCD10A1/blob/master/MCD10A1.js
	# In case we switch to the surrounding year, we have to increase the year counter for the end date, that is why we need to specify the Startyear and endYear
	yearStart = year
	yearEnd = year
	# Convert the information on year, startMonth, endMonth to a date for the filter --> define lastday of endMonth based on how many days are in that month
	if endMonth in [4, 6, 9, 11]:
		lastDay = 30
	if endMonth in [1, 3, 5, 7, 8, 10, 12]:
		lastDay = 31
	if endMonth == 2:
		lastDay = 28
	start = ee.Date.fromYMD(yearStart, startMonth, 1)
	end = ee.Date.fromYMD(yearEnd, endMonth, lastDay)
	# Function to calculate the maximum value of the two collections
	def CalculateMax(feature):
		# load feature and set start time when mapping
		img = ee.Image(feature)
		startTime = img.select('NDSI_Snow_Cover').get('system:time_start')
		# assign 0 values (which can be confused with NA) a small negative value for both bands
		b1c = img.expression('b1 == 0 ? -10 : b1', {'b1': img.select('NDSI_Snow_Cover')})
		b2c = img.expression('b1 == 0 ? -10 : b1', {'b1': img.select('NDSI_Snow_Cover_1')})
		# Take the maximum value of the remapped data while unmasking (assigning 0 to NA) the data
		maxval = b1c.unmask(0).max(b2c.unmask(0))
		# update the mask (set all 0 values to NA)
		maxval = maxval.updateMask(maxval.neq(0))
		# substitute in the original 0 values, which are currently registered as -10
		maxval = img.expression('b1 == -10 ? 0 : b1', {'b1': maxval})
		# associate the start time with the new image and return the data
		maxval = maxval.set('system:time_start',startTime)
		return maxval
	# Function to stick two bands together which are linked with an inner join
	def ConcatBands(feature):
		return ee.Image.cat(feature.get('primary'),feature.get('secondary'))

	# Get the two image collections and create an additional value for the system time
	terraCollection = ee.ImageCollection('MODIS/006/MOD10A1').select('NDSI_Snow_Cover').filterDate(start, end).filterBounds(roi).sort('system:time_start')
	aquaCollection = ee.ImageCollection('MODIS/006/MYD10A1').select('NDSI_Snow_Cover').filterDate(start, end).filterBounds(roi).sort('system:time_start')
	filterTimeEq = ee.Filter.equals(leftField='system:time_start', rightField='system:time_start')

	# // create a collection of both MOD/MYD data matched
	innerJoin = ee.Join.inner() # joined per band using an inner join
	innerJoinedCollection = innerJoin.apply(terraCollection, aquaCollection, filterTimeEq) # Apply the join
	joinedCollection = innerJoinedCollection.map(ConcatBands) # combine matching images into one image with (2) bands

	# calculate the maximum value across the two bands MOD / MYD
	yearlyCollection = joinedCollection.map(CalculateMax)

	# apply the reducer
	red = ee.ImageCollection(yearlyCollection).reduce(ee.Reducer.mean()).int()

	return red

def export_Variables(tile):
	roi = tiles.filterMetadata(tilevar, 'equals', tile)
	# To safe space, multiply floating values by 10000

	# Vegetation indices from Landsat
	indices = Calculate_Landsat_Seasonal_Mean(year=2020, startMonth=4, endMonth=9, roi=roi).int()

	# Topography measures from SRTM
	elevation = ee.Image("USGS/SRTMGL1_003").select('elevation').clip(roi).int()
	slope = ee.Terrain.slope(elevation).clip(roi).int()
	aspect = ee.Terrain.aspect(elevation).clip(roi).int()
	stack = indices.addBands(elevation).addBands(slope).addBands(aspect)


	# Snow cover from MODIS
	for month in np.arange(1, 12+1, 1).tolist():
		stack = stack.addBands(Calculate_Mean_NDSI(year=2020, startMonth=month, endMonth=month, roi=roi))

	# Rename the bands
	old_BN = stack.bandNames()
	new_BN = ["NDVI", "NDMI", "EVI",  "tcW", "tcB", "tcG", "Elev", "Slope", "Aspect",
			  "NDSI_Jan", "NDSI_Feb", "NDSI_Mar", "NDSI_Apr", "NDSI_May", "NDSI_Jun", "NDSI_Jul", "NDSI_Aug", "NDSI_Sep", "NDSI_Oct", "NDSI_Nov", "NDSI_Dec"]
	stack = stack.select(old_BN).rename(new_BN)

	description = 'export_Region_' + str(tile)
	fileNamePrefix = 'Region_' + str(tile) + "_Variables"
	GEE_Folder = 'Baumi_GEE'

	task = ee.batch.Export.image.toDrive(
		image=stack,
		description=description,
		folder=GEE_Folder,
		fileNamePrefix=fileNamePrefix,
		region=roi.geometry().getInfo()['coordinates'],
		scale=250)#,
		# maxPixels=3784216672400)

	task.start()


# ####################################### START PROCESSING #################################################### #
# (0) Filter warnings and intialize GEE and GoogleDrive
print("Initialize Google Earth Engine")
warnings.filterwarnings("ignore", category=RuntimeWarning)
ee.Initialize()
gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)

# (1) CLEAN all tiles that are at the moment stored on GoogleDrive before we start all the processes
print("Delete remaining tiles on google drive")
drive_list = drive.ListFile({'q': "'0B9hZR9DKK3xRS3phZnhQcVlwVHc' in parents and trashed=false"}).GetList()
for file in drive_list:
	file_id = drive.CreateFile({'id': file['id']})
	file_id.Delete()

# (2) Convert shpfile into feature collection
print("Convert tiles into Earth-Engine Feature Collection")
featList = []
LYR = studyArea.GetLayer()
FEAT = LYR.GetNextFeature()
while FEAT:
	# Get the feature geometry and its ID
	geom = FEAT.GetGeometryRef()
	featID = FEAT.GetField(tilevar)
	# Build the EE-feature via the json-conversion
	geom_json = json.loads(geom.ExportToJson())
	geom_coord = geom_json['coordinates']
	geom_EE = ee.Geometry.Polygon(coords=geom_coord)
	feat_EE = ee.Feature(geom_EE, {"Id": featID})
	# Add to the list, take next feature
	featList.append(feat_EE)
	FEAT = LYR.GetNextFeature()
# Convert the featList into an EE FeatureCollection
tiles = ee.FeatureCollection(ee.List(featList))
features = ee.Feature(tiles.first()).propertyNames().sort()  # Something Julian did in his script
tile_names = tiles.distinct(tilevar).aggregate_array(tilevar).getInfo()
# time.sleep(1)
print("")
print("Submitting jobs to GEE")

for tile in tile_names:
	export_Variables(int(tile))
	task_list = str(ee.batch.Task.list())
	n_running = task_list.count('RUNNING')
	n_ready = task_list.count('READY')
	n_tasks = n_running + n_ready
	drive_list = drive.ListFile({'q': "'0B9hZR9DKK3xRS3phZnhQcVlwVHc' in parents and trashed=false"}).GetList()
	for file in drive_list:
		file_id = drive.CreateFile({'id': file['id']})
		fname = file["title"]  # This is the filename the file is stored on google drive
		outName = output_folder + fname
		file_id.GetContentFile(outName)
		file_id.Delete()

time.sleep(60)
print("--------------------------------------------------------")
print("Waiting for, and downloading remaining files from the server")
drive_list = drive.ListFile({'q': "'0B9hZR9DKK3xRS3phZnhQcVlwVHc' in parents and trashed=false"}).GetList()
task_list = str(ee.batch.Task.list())
tasks_running = task_list.count('RUNNING')
while len(drive_list) > 0 or tasks_running > 0:
	for file in drive_list:
		file_id = drive.CreateFile({'id': file['id']})
		fname = file["title"]  # This is the filename the file is stored on google drive
		outName = output_folder + fname
		file_id.GetContentFile(outName)
		file_id.Delete()
	drive_list = drive.ListFile({'q': "'0B9hZR9DKK3xRS3phZnhQcVlwVHc' in parents and trashed=false"}).GetList()
	task_list = str(ee.batch.Task.list())
	tasks_running = task_list.count('RUNNING')

# ##################################### END TIME-COUNT AND PRINT TIME STATS#################################### #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")