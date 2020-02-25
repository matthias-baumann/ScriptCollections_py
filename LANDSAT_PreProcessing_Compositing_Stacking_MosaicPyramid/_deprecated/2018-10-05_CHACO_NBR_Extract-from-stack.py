# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
from gdalconst import *
import time
import baumiTools as bt
import gdal
import os
from tqdm import tqdm
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ####################################### FUNCTIONS, FOLDER PATHS AND BASIC VARIABLES ######################### #
inRoot = "G:/CHACO/_LANDSAT/annual_Metrics/"
outRoot = "O:/Student_Data/Otto_Jana/Composites/"
years = range(1985, 2018, 1)
tiles = [335, 336, 337, 338, 339, 360, 361, 362, 363, 364, 385, 386, 387, 388, 389, 411, 412, 413]
bands = [43, 44, 45, 46, 47, 48, 49]
drvMemR = gdal.GetDriverByName('MEM')
def BuildVRT(folder, ext, outVRT, pyramids=True):
	# Get the files from the folder
	finalFileList = []
	file_list = os.listdir(folder)
	for file in file_list:
		if file.endswith(ext):
			filepath = folder + file
			finalFileList.append(filepath)
	# write files to a temporary txt-file
	outTXT = outVRT
	outTXT = outTXT.replace(".vrt", ".txt")
	f_open = open(outTXT, "w")
	for item in finalFileList:
		f_open.write(item + "\n")
	f_open.close()
	# Build the VRT
	command = "gdalbuildvrt.exe -vrtnodata 0 -input_file_list " + outTXT + " " + outVRT
	os.system(command)
	# Build the pyramids, if the argument is specified accordingly
	if not pyramids == False:
		command = "gdaladdo.exe " + outVRT + " 2 4 8 16 32 64"
		os.system(command)
	# Remove the txt.file
	os.remove(outTXT)
# ####################################### PROCESSING ########################################################## #
# Loop through the years
for yr in years:
	print("Copying tiles for year:", str(yr))
# create the output-folder for that year
	outFolder = outRoot + str(yr) + "/"
	bt.baumiFM.CreateFolder(outFolder)
# Now loop through the tiles to extract the different bands
	for tile in tqdm(tiles):
	# Define the filenames of the tiles
		inTile = inRoot + str(yr) + "/" + "tileID_" + str(tile) + ".tif"
		outTile  = outFolder + "tileID_" + str(tile) + ".tif"
	# Check if file does not exist, only in that case do the copying
		if not os.path.exists(outTile):
		# Open input-file, get properties
			inDS = gdal.Open(inTile)
			pr = inDS.GetProjection()
			gt = inDS.GetGeoTransform()
			cols = inDS.RasterXSize
			rows = inDS.RasterYSize
			#dType = inDS.GetRasterBand(1).DataType
		# Create output-dataset
			outDS = drvMemR.Create('', cols, rows, len(bands), GDT_Int16)
			outDS.SetProjection(pr)
			outDS.SetGeoTransform(gt)
		# Now loop through bands and copy them
			b_out = 1
			for b_in in bands:
				inARR = inDS.GetRasterBand(b_in).ReadAsArray(0, 0, cols, rows)
				outDS.GetRasterBand(b_out).WriteArray(inARR, 0, 0)
				b_out += 1
		# Write file to disc
			bt.baumiRT.CopyMEMtoDisk(outDS, outTile)
# Create the VRTs and build the pyramids
for yr in years:
	print("Building pyramids for year:", str(yr))
	inFolder = outRoot + str(yr) + "/"
	outVRT = outRoot + "Mosaic_" + str(yr) + ".vrt"
	BuildVRT(inFolder, ".tif", outVRT)


# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")