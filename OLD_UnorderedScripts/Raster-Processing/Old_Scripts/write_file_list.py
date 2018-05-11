# script to list all landsat archives in a directory
# example command to run script: C:\tar_extract.py C:\landsat_imagery\ C:\landsat_imagery\list.txt

# import system modules
import os
import sys

# argument for location of directory containing all .tar.gz files, and nothing but .tar.gz files
# include final "\" at end of argument
dir = sys.argv[1]

# argument for textfile location and name
txtfile = sys.argv[2]

# open textfile and write
file = open(txtfile,"w")

# defines directory list
dirList = os.listdir(dir)

# loop iterating through all items in directory, creating new folders, and unpackaging .tar.gz files into new folders
for fname in dirList:
	direct = fname[:21]        # 21 denotes number of characters to include for directory name; excludes .tar.gz
	file.writelines(direct)
	file.writelines("\n")
	#os.mkdir(dir + direct)
	#print "Processing File " + fname
	#t = tarfile.open(dir + fname)
	#t.extractall(dir + direct)
file.close()
