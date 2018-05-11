# Tool that converts the downloaded metafile from the EARTHEXPLORER-server into a csv-file, organizing the image information in the way
# we did it for the Carpathian project. 
# Simply download the xml-File from the landsat-metadata website (landsat.usgs.gov/consumer.php)
# Enter on the website the parameters needed, including ALL landsat footprints that you wish to be analyzed. They can be all bundled in one.
# Call the py-Script with the instructions below.
# The result will be 
# (1) a general 'thumbnail-folder' that gets generated at the first run and all thumbnails will be copied into it.
# (2) A csv-file for each landsat-footprint SEPARATELY

# Within the csv-file, replace in the column "thumbnail" in every row the ';' for a ',', so that the hyperlink gets generated and save the
# file into a new excel-spreadsheet. Add to this spreadsheet all other csv-sheets, if you wish!
# HERE MOST LIKELY AN UPDATE WILL COME SOON, SO THAT THE SCRIPT WILL DO THESE STEPS FOR THE USER, I.E., CREATING A XLS-FILE WITH SPREADSHEETS
# FOR EACH FOOTPRINT

# Initial parametrization needs the foolowing information (in this order) in the command-line, separated by a space:
# (1) call the py-script
# (2) path and filename of the metadatafile, that you downloaded from the usgs
# (3) root-directory for the Landsat-processig (e.g., E:\Landsat\) --> all other folders get then generated autom.
# An example command in the command prompiwould be:
# "F:\...\\\Read-in_GLVIS-metafile_version-20110526.py c:\...\metadata.xml e:\Landsat\


 #IMPORT SYSTEM MODULES
from __future__ import division
from math import sqrt
import sys, string, os#, arcgisscripting
import time
import urllib.request # to download the images from the web
#import xlwt		# need to write xls-Files, install first the package, downloaded from http://pypi.python.org/pypi/xlwt

starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())

# COMMAND LINE ARGUMENTS AND SUBSEQUENT CREATION OF FOLDERS INCLUDING THE FINAL EXCEL-FILE
if len(sys.argv) < 2:
	print("Path to input xml-file")
	exit(0)
	
input = sys.argv[1]
outputDir = sys.argv[2]

print("Input-dataFile: ", input)
print("OutputFolder: ", outputDir)
print("Start building lists, and create files and folders for output")

outFile = outputDir + ".csv"
thumbFolder = outputDir
thumbFolder = thumbFolder + "Thumbnails\\"
if not os.path.lexists(thumbFolder):
	os.makedirs(thumbFolder)#, 0777)


# BUILD LISTS AND FILL THEM WITH INFORMATION
pathList = []
rowList = []
pathRowList = []
dateList = []
yearList = []
monthList = []
dayList = []
sensorList = []
cloudList = []
linkList = []
sceneIDList = []
csvList = []

infoFile = open(input, "r")
for line in infoFile:
	if line.find("path") >= 0:
		pos1 = line.find(">")
		pos2 = line.rfind("<")
		path = line[pos1+1:pos2]
		if len(path) == 2:
			path = "0" + path
		pathList.append(path)

	if line.find("/row") >= 0:
		pos1 = line.find(">")
		pos2 = line.rfind("<")
		row = line[pos1+1:pos2]
		if len(row) == 2:
			row = "0" + row
		rowList.append(row)

	if line.find("acquisitionDate") >= 0:
		pos1 = line.find(">")
		pos2 = line.rfind("<")
		date = line[pos1+1:pos2]
		date = str(date)
		dateList.append(date)
		year = line[pos1+1:pos1+5]
		year = str(year)
		yearList.append(year)
		month = line[pos1+6:pos1+8]
		month = str(month)
		monthList.append(month)
		day = line[pos1+9:pos1+11]
		day = str(day)
		dayList.append(day)

	if line.find("cloudCoverFull") >= 0:
		pos1 = line.find(">")
		pos2 = line.rfind("<")
		cloud = line[pos1+1:pos2]
		cloud = str(cloud)
		cloudList.append(cloud)

	if line.find("sceneID") >= 0:
		pos1 = line.find(">")
		pos2 = line.rfind("<")
		sceneID = line[pos1+1:pos2]
		sceneID = str(sceneID)
		sceneIDList.append(sceneID)

	if line.find("sensor") >= 0:
		pos1 = line.find(">")
		pos2 = line.rfind("<")
		sensor = line[pos1+1:pos2]
		sensor = str(sensor)
		sensorList.append(sensor)

	if line.find("<browseURL>http") >= 0:
		pos1 = line.find(">")
		pos2 = line.rfind("<")
		link = line[pos1+1:pos2]
		link = str(link)
		linkList.append(link)

print("Lists ready. Starting downloading the thumbnails")

for link in linkList:
	url = link
	filename = thumbFolder
	pos1 = link.rfind("/")
	pos2 = link.rfind(".jpg")
	tempname = link[pos1+1:pos2]
	filename = filename + tempname
	filename = filename + ".jpg"
	urllib.request.urlretrieve(url, filename)
	filename = str(filename)
	print(url)
	csvLink = "=HYPERLINK(\".\\Thumbnails\\" + tempname + ".jpg\";\"pic\")"
	csvLink = str(csvLink)
	csvList.append(csvLink)

for scene in sceneIDList:
	i = sceneIDList.index(scene)
	pathRow = str(pathList[i]) + str(rowList[i])
	pathRow = str(pathRow)
	pathRowList.append(pathRow)
	pathRowListsub = list(set(pathRowList))


# BUILDING THE CSV-Files
for pathRow in pathRowListsub:
	out = outFile.replace(".csv","")
	out = out + pathRow + ".csv"
	out = open (out, "w")
	out.write("Path,Row,AcquisitionDate,AcquisitionYear,AcquisitionMonth,AcquisitionDay,Sensor,CloudCoverage,Thumbnail,SceneID,Downloaded\n")
	for sceneID in sceneIDList:
		i = sceneIDList.index(sceneID)		# this returns the current element index of the first list - use to grab same element in other lists
		PR = pathList[i] + rowList[i]
		if PR == pathRow:
			out.write(pathList[i] + "," + rowList[i] + "," + dateList[i] + "," + yearList[i] + "," + monthList[i] + "," + dayList[i] + "," + sensorList[i] + "," + cloudList[i] + "," + csvList[i] + "," + sceneID + "," + "NO" + "\n")
	out.close()



endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())

print("start: ", starttime)
print("end: ", endtime)
print("!!! Open the csv-File, go to the 'Thumbnails'-column and replace the ';' with a regular ','. This ensures that all links are getting set correctly. Try also to reformat the date-column if you wish.")



