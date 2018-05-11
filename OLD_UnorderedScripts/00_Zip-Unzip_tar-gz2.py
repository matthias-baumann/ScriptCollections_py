# ######################################## LOAD REQUIRED MODULES ############################################### #
# IMPORT SYSTEM MODULES
import os
import time
import tarfile
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:", starttime)
print("")



def unzip(folder):
	print("--------------------------------------------------------")
	RAW_List = os.listdir(str(folder))
	for file in RAW_List:
		if file.find("Thumbs.db") < 0:
			output = folder + file + "\\"
			output = output.replace(".tar.gz","")
			print("Extracting tar-archive:", file)
			archiveName = folder + file
			tar = tarfile.open(archiveName, "r")
			list = tar.getnames()
			for file in tar:
				tar.extract(file, output)
			tar.close()
			file = None
					

			

# ####################################### RUN THE MODULES AND CALL THE FUNCTIONS ############################## #	

call = sys.argv[1]
in_folder = sys.argv[2]

if call == "zip":
	zip(in_folder)
else:
	if call == "unzip":
		unzip(in_folder)
	else:
		print("Incorrect call for function. Use 'zip' or 'unzip' for processing")
		exit(0)


# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #		
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: ", starttime)
print("end: ", endtime)
print("")