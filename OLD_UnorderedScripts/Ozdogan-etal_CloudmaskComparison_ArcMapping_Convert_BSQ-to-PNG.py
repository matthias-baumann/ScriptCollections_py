# ######################################## BEGIN OF HEADER INFROMATION AND LOADING OF MODULES ########################################
# IMPORT SYSTEM MODULES
import arcpy
import os
import time

# ##### SET TIME-COUNT AND HARD-CODED FOLDER-PATHS #####
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("")
print("Starting process, time:", starttime)
print("")

# SET FOLDERS WHERE WE SEARCH THROUGH
base_folder = "E:\\tempdata\\mbaumann\\Cloudmask_Comparison\\Algorithm-Outputs\\"
mxdFile = "E:\\tempdata\\mbaumann\\Cloudmask_Comparison\\map.mxd"
tmpLayer = "E:\\tempdata\\mbaumann\\Cloudmask_Comparison\\tmpLayer.lyr"

# GENERATE LIST FOR FOLDERS WE PROCESS
folder_list = os.listdir(base_folder)
# LOOP THROUGH THESE FOLDERS
for folder in folder_list[:]:
	work_folder = base_folder + folder + "\\"
	# CREATE LIST FOR THE FILES WE ARE GOING TO PROCESS
	file_list = os.listdir(work_folder)
	# REMOVE .hdr-FILES IN THE LIST
	for file in file_list[:]:
		if file.find(".hdr") >= 0 or file.find("Thumbs") >= 0 or file.find(".png") >= 0:
			file_list.remove(file)
	# NOW LOOP THROUGH THE FILES IN LIST AND CONVERT THEM INTO PNG-FILES
	for file in file_list[:]:
		input = work_folder + file
		# DEFINE INPUT AND OUTPUT
		output = input
		output = output.replace(".bsq","_png.png")
		print(input)
		# BUILD THE ARC-MAP_DOCUMENT  AND CONVERT THE RASTER INTO A LAYER
		mxd = arcpy.mapping.MapDocument(mxdFile)
		Lyr = arcpy.MakeRasterLayer_management(input, tmpLayer)
		layer = Lyr.getOutput(0)
		# ADD LAYER TO MAP-DOCUMENT AND EXPORT THE DOCUMENT
		df = arcpy.mapping.ListDataFrames(mxd)[0]
		spatialRef = arcpy.Describe(Lyr).spatialReference
		df.spatialReference = spatialRef
		arcpy.mapping.AddLayer(df, layer)
		arcpy.RefreshActiveView()
		
		arcpy.mapping.ExportToPNG(mxd, output, df, df_export_width = 1200, df_export_height = 1200, resolution = 600)

	print("")
	exit(0)
	
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: ", starttime)
print("end: ", endtime)
print("")