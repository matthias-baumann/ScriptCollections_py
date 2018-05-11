import os
import time, datetime
from ZumbaTools.Conversion_Tools import *
from ZumbaTools.FileManagement_Tools import *
from ZumbaTools.Raster_Tools import *
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ############################################################################################################# #
# (1) RASTER-FILES
# (1-1) REPROJECT FILES TO COMMON COORDINATE SYSTEM
inputFolder_independent = "T:/Smaliychuk/to_Tolik/InputFiles_AsTIFF/Independent_var/"
inputFolder_dependent = "T:/Smaliychuk/to_Tolik/InputFiles_AsTIFF/Dependent_var/"
print("Reprojecting...")
indep_inlist = GetFilesInFolderWithEnding(inputFolder_independent, ".tif")
for file in indep_inlist:
    output = file
    output = output.replace(".tif","_ETRS89_LAEA.tif")
    Reproject_EPSG(file, output, 3035, "near")
dep_inlist = GetFilesInFolderWithEnding(inputFolder_dependent, ".tif")
for file in dep_inlist:
    output = file
    output = output.replace(".tif","_ETRS89_LAEA.tif")
    Reproject_EPSG(file, output, 3035, "near")

# (1-2) CLIP FILES TO MINIMUM EXTENT
# Build overall list of all files, get extent
indep_inlist = GetFilesInFolderWithEnding(inputFolder_independent, "LAEA.tif")
dep_inlist = GetFilesInFolderWithEnding(inputFolder_dependent, "LAEA.tif")
print("Get Minimum Extent...")
mergedList = indep_inlist + dep_inlist
minExtent = GetMinimumRasterExtent(mergedList)

# Clip files to extent
print("Clip files...")
for file in mergedList:
    # Clip the file
    output = file
    output = output.replace(".tif", "_clip.tif")
    ClipMask_byCoordinates(file, output, minExtent[0], minExtent[2], 0)
    # Delete the unclipped files
    os.remove(file)

# (1-3) RESAMPLE INTO THE DIFFERENT RESOLUTIONS
print("Resampling rasters...")
root_output = "T:/Smaliychuk/to_Tolik/"
resolutions = [1000, 2500, 5000]
for res in resolutions:
    print("Resolution: " + str(res) + "m")
    res_folder = root_output + str(res/1000) + "km/"
    CreateFolder(res_folder)
    # Independent Variables
    print("Independent Variables")
    out_folder = res_folder + "Independent_var/"
    CreateFolder(out_folder)
    indep_inlist = GetFilesInFolderWithEnding(inputFolder_independent, "clip.tif")
    for file in indep_inlist:
        p = file.rfind("/")
        outfile = file[p+1:len(file)]
        outfile = outfile.replace(".tif", "_" + str(res) + "m.tif")
        outpath = out_folder + outfile
        Resample(res, "average", file, outpath)
    # Dependent Variables
    print("Dependent Variables")
    out_folder = res_folder + "Dependent_var/"
    CreateFolder(out_folder)
    dep_inlist = GetFilesInFolderWithEnding(inputFolder_dependent, "clip.tif")
    for file in dep_inlist:
        p = file.rfind("/")
        outfile = file[p+1:len(file)]
        outfile = file[p+1:len(file)]
        outfile = outfile.replace(".tif", "_" + str(res) + "m.tif")
        outpath = out_folder + outfile
        Resample(res, "average", file, outpath)

# (2) CONVERT THE VECTOR FILES
in_shp = "T:/Smaliychuk/to_Tolik/Raions_490m.shp"
# (2-1) CONVERT SHAPEFILE INTO COORDINATE-SYSTEM
print("Re-project shapefile...")
proj_shp = "T:/Smaliychuk/to_Tolik//Raions_490m_ETRS89_LAEA.shp"
Reproject_EPSG(in_shp, proj_shp, 3035, "NN")
# (2-2) CONVERT THE SHAPEFILE TO RASTER-FILES FOR EACH ATTRIBUTE FIELD FROM LIST AND FOR EACH RESOLUTION
fields = ["Pop_change", "Pop_dnst", "Sh_y_el_pn", "Unempl", "Yld_01_06", "Mn_f_01_06", "Mn_f_01_06",
          "Or_f_01_06", "Mch_01_06", "Rn_code", "Obl_code", "Pd_01_06", "P_ch_01_06", "Y_el_01_06",
          "Unem_01_06"]
print("Rasterize shp-file...")
for res in resolutions:
    print("Resolution: " + str(res) + "m")
    out_folder = root_output + str(res/1000) + "km/Independent_Var/"
    for field in fields:
        p = proj_shp.rfind("/")
        outfile = proj_shp[p+1:len(proj_shp)]
        outfile = proj_shp[p+1:len(proj_shp)]
        out_path = out_folder + outfile
        out_path = out_path.replace(".shp", "_" + field + "_" + str(res) + "m.tif")
        Rasterize_Shp_by_attribute(res, field, proj_shp, out_path, minExtent[0], minExtent[2])


print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: ", starttime)
print("end: ", endtime)
print("")