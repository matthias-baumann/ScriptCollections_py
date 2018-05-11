#!/usr/bin/env python
"""
Process_GLOVIS_metafile.py

   Description:
      This is a tool that converts the downloaded metafile from the EARTHEXPLORER-server
       into a xls-file with organized image information.
 
   Author:            Mathias Bauman
                      Silvis Lab
					  Department of Forestry & Wildlife Ecology
					  UW Madison
   Creation Date:     08-12-2011
   Version:			  1.0

   How to use:
       1. Go to the landsat-metadata website (landsat.usgs.gov/consumer.php).
       2. Fill in the webform with the required parameters; include ALL landsat 
        	footprints to be analyzed. They will all be bundled into one xml file.
       3. Select "Get Metadata" and download the xml-File to your hard drive.
       4. Call the py-Script (Process_GLOVIS_metafile.py):

	        Process_GLOVIS_metafile.py <path\filename of metadata> <path where files will be written>
	
            (e.g.  .\Process_GLOVIS_metafile.py c:\...\CR_metadata.xml d:\...\CR_landsat        )

   Return values:
       1. A 'thumbnail-folder' into which all thumbnails will be copied.
       2. An xls-file with a separate worksheet for each landsat-footprint.
    
   Dependencies:
         Public:     os, sys, math, string, time, urllib (to download images from the web),
	             xlwt (to write xls spreadsheets), __future__, arcgisscripting
   
Updates:
   Author:            Jordan Muss
                      Geographic Information Science Center of Excellence
					  South Dakota Stae University
   Mod. Date:         10-02-2012 
   Version:			  2.0
                Refined code to use a class structure to store the data. Put the
                line parsing into the class. Added a method that will create an index
				and sort it using the year as the criteria. Changed the code to write to
				an excel workbook instead of a CSV file

To Do:  1. Modify the class to parse the data file using the "<metaData>" tag. This should
           eliminate any potential problems with mismatches in data.
		2. Make the indexing method more general so that the data can be indexed using any field.
		3. Allow the script to create a separate worksheet for each scene (tile).
		4. Allow the user to provide a bounding box to subset the scene for analysis of
		   the quality of the scene (e.g. cloud coverage within the subset area).
		5. Allow the user to set a cloud threshhold for the subset area.
"""

 #IMPORT SYSTEM MODULES
from __future__ import division
from operator import itemgetter, attrgetter
from math import sqrt
import sys, string, os, arcgisscripting
import time
import urllib
import xlwt

class dataClass:
    def __init__(self):
	self.idx = []
        self.path = []
	self.row = []
	self.date = []
	self.year = []
	self.month = []
	self.day = []
	self.sensor = []
	self.cloud = []
	self.link = []
	self.sceneID = []
	self.csv = []
    def add(self, line):
	pos1 = line.find(">")
	pos2 = line.rfind("<")
	word = line[pos1+1:pos2]
	if line.find("path") >= 0:
	    if len(word) == 2:
		word = "0" + word
	    self.path.append(word)
    
	if line.find("/row") >= 0:
	    if len(word) == 2:
		word = "0" + word
	    self.row.append(word)
    
	if line.find("acquisitionDate") >= 0:
	    self.date.append(word)
	    self.year.append(word[0:4])
	    self.month.append(word[5:7])
	    self.day.append(word[8:10])
    
	if line.find("cloudCoverFull") >= 0:
	    self.cloud.append(str(word))
    
	if line.find("sceneID") >= 0:
	    self.sceneID.append(word)
    
	if line.find("sensor") >= 0:
	    self.sensor.append(word)
    
	if line.find("<browseURL>http") >= 0:
	    self.link.append(word)

    def index(self):
	tmp = []
	for i in range(len(self.date)):
	    tmp.append([i,self.date[i]])
	tmp.sort(key=itemgetter(1))
	for i in range(len(self.date)):
	    self.idx.append(tmp[i][0])

landsatData = dataClass()
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())

# COMMAND LINE ARGUMENTS AND SUBSEQUENT CREATION OF FOLDERS INCLUDING THE FINAL EXCEL-FILE
if len(sys.argv) < 2:
	print "Path to input xml-file "
	exit(0)
	
inFile = sys.argv[1]
outPath = sys.argv[2]
outDirEnd = outPath.rfind("\\")
#outDirBeg = outPath[0:outDirEnd].rfind("\\")
xlsFile = outPath[(outDirEnd + 1):(len(outPath) - 1)] + '.xls'
thumbFolder = outPath + "Thumbnails\\"
linkHead = "HYPERLINK(\".\\" + outPath[(outDirEnd + 1):(len(outPath))] + "Thumbnails\\"

print "Input data file: " + inFile
print "Output folder: " + thumbFolder
print "Output file: " + xlsFile
print "Start building lists, and create files and folders for output"

if not os.path.lexists(thumbFolder):
	os.makedirs(thumbFolder, 0777)


# Build the lists to be filled with path-row and thumbnail information:
pathRowList = []
jpgList = []

infoFile = open(inFile, "r")
for line in infoFile:
    landsatData.add(line)

print "Lists ready. Starting downloading the thumbnails"
landsatData.index()

for i in landsatData.idx:
    url = landsatData.link[i]
    pathRowList.append(landsatData.path[i] + landsatData.row[i])
    filename = thumbFolder
    tempname = url[url.rfind("/")+1:url.rfind(".jpg")]
    filename = filename + tempname + ".jpg"
    urllib.urlretrieve(url, filename)
    filename = str(filename)
    print url
    jpgList.append(linkHead + tempname + ".jpg\",\"pic\")")
pathRowList = set(pathRowList)

# Build the xls-File:
wbk = xlwt.Workbook()
for pathRow in pathRowList:
    sheet = wbk.add_sheet("Path_" + pathRow[0:2] + "_Row_" + pathRow[3:5])
    row = 0
    sheet.write(row,0,"Path")
    sheet.write(row,1,"Row")
    sheet.write(row,2,"AcquisitionDate")
    sheet.write(row,3,"AcquisitionYear")
    sheet.write(row,4,"AcquisitionMonth")
    sheet.write(row,5,"AcquisitionDay")
    sheet.write(row,6,"Sensor")
    sheet.write(row,7,"CloudCoverage")
    sheet.write(row,8,"Thumbnail")
    sheet.write(row,9,"SceneID")
    sheet.write(row,10,"Downloaded")
    """ If there is more than one scene ID then a loop should be added to re-sort
        the dates for each scene.                                                """
    for i in landsatData.idx:
	PR = landsatData.path[i] + landsatData.row[i]
	if PR == pathRow:
	    row = i + 1
	    sheet.write(row,0,landsatData.path[i])
	    sheet.write(row,1,landsatData.row[i])
	    sheet.write(row,2,landsatData.date[i])
	    sheet.write(row,3,landsatData.year[i])
	    sheet.write(row,4,landsatData.month[i])
	    sheet.write(row,5,landsatData.day[i])
            sheet.write(row,6,landsatData.sensor[i])
            sheet.write(row,7,landsatData.cloud[i])
	    sheet.write(row,8,xlwt.Formula(jpgList[i]))
            sheet.write(row,9,landsatData.sceneID[i])
            sheet.write(row,10,"NO")
wbk.save(xlsFile)

print "start: " + starttime
print "end: " + time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
