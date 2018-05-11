# ####################################### LOAD REQUIRED MODULES ############################################### #
import sys, string, os
import time, datetime
import urllib.request
from urllib.request import urlopen
import urllib.request
import re
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:", starttime)
print("")
# ####################################### SET INPUT VARIABLE ################################################# #
server_url = "http://e4ftl01.cr.usgs.gov/"
local_folder = "D:/MODIS_Phenology/"
MOTA_MOLT = "MOLT/"
dl_product = "MOD09A1.005"
Years_of_Interest = [2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012]
Months_of_Interest = [1,2,3,4,5,6,7,8,9,10,11,12]
MODIS_tile = ["h11v05", "h09v04", "h11v03", "h11v04", "h12v04", "h13v04"]
# ####################################### DO THE OPERATION ################################################### #

# (1) BUILD THE INITIAL LIST FOR SCENES WE WANT TO DOWNLOAD BASED ON CRITERIA ####

# (1-A) GET THE AVAILABLE DATE-LIST FROM THE SERVER AND COMPARE TO CRITERIA (YEARS,MONTHS) ####
# Get the available dates from "MODIS_server"
print("Check if server is online")
MODIS_server = server_url + MOTA_MOLT + dl_product
response = str(urlopen(MODIS_server).read())

print("Building List of Scenes to Download")
e = response.split(' alt="[DIR]"> <a href=')
e = e[2:len(e)]
# Check for dates we want to download
datelist_server = []
for item in e:
	date = item[1:11]
	y = int(item[1:5])
	m = int(item[6:8])
	if y in Years_of_Interest and m in Months_of_Interest[:]:
		datelist_server.append(date)
# (1-B) NOW SEARCH THROUGH THE DATES AND SELECT THE FILES (HDF) BASED ON THE TILE-CRITERIA
hdf_list = []
for date in datelist_server[:]:
	MODIS_server_date = server_url + MOTA_MOLT + dl_product + "/" + date
	response = str(urlopen(MODIS_server_date).read())
	e = response.split("<a href=")
	# Build and fill list with all hdf-files on the server
	for item in e:
		if item.find(".hdf") >= 0 and item.find("xml") < 0:
			p = item.find(".hdf")
			hdf = item[1:p+4]
			p = hdf.find(".h")
			tile = hdf[p+1:p+7]
			if tile in MODIS_tile:
				downloadPath = MODIS_server_date + "/" + hdf
				hdf_list.append(downloadPath)
print("DONE")
print("")
# (2) NOW DOWNLOAD THE FILES TO THE LOCAL FOLDER				
for item in(hdf_list):
	online_path = item
	p = item.rfind("/")
	online_file = item[p+1:len(item)]
	print("Downloading file: " + online_file)
	local_path = local_folder + online_file
	if not os.path.exists(local_path):
		try:
			urllib.request.urlretrieve(online_path, local_path)
		except:
			print("Could not download: " + online_file)
			
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: ", starttime)
print("end: ", endtime)
print("")





# #####################################################################################################################################################################################
# ############################################################# OLD FTP SCRIPT VERSION ################################################################################################
# local_folder = "E:/MODIS/"
# dl_product = "MOLT/MOD11A1.005"
# Years_of_Interest = [2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012]
# Months_of_Interest = [1,2,3,4,5,6,7,8,9,10,11,12]
# MODIS_tile = ["h19v03"]
# ####################################### DO THE OPERATION ################################################### #

# (1) Establish ftp Connection, retrieve folders on server
# ftp = ftplib.FTP_TLS("e4ftl01.cr.usgs.gov")
# ftp.login()
#ftp.login("anonymous", "thisisme")
# ftp.cwd(dl_product)
# data = []
# ftp.dir(data.append)
# dirnames = [i.split()[-1] for i in data[1:]]

# (2) Do the Year-Month-Selection based on Input-Variable
# imageList = []
# for dir in dirnames:
	# p = dir.find(".")
	# y = int(dir[0:p])
	# p = dir.rfind(".")
	# m = int(dir[p-2:p])
	# if y in Years_of_Interest and m in Months_of_Interest:
		# imageList.append(dir)

# (3) Download the files MODIS-tile by MODIS-tile
# for tile in MODIS_tile:
	# for dir in imageList:
		# ftp.cwd(dir)
		# this = []
		# ftp.dir(this.append)
		# filelist = [i.split()[-1] for i in this[1:]]
		# for file in filelist:
			# if tile in file and file.find(".hdf") >= 0 and file.find(".xml") < 0:
				# print("Downloading: " + file)
				# local = os.path.join(local_folder, file)
				# lf_open = open(local, "wb")
				# ftp.retrbinary("RETR " + file, lf_open.write)
				# lf_open.close()
				# ftp.cwd('..')					
