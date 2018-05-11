# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import gdal
from gdalconst import *
import csv
import numpy as np
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ####################################### HARD-CODED FOLDERS AND FILES ######################################## #
in_csv = "G:/CHACO/_ANALYSES/Percent_TreeCover_2013/MasterD.csv"
out_spec = "G:/CHACO/_ANALYSES/Percent_TreeCover_2013/PercentTreeCover_spectra_20160115.bsq"
out_labels = "G:/CHACO/_ANALYSES/Percent_TreeCover_2013/PercentTreeCover_labels_20160115.bsq"
# ####################################### PROCESSING ########################################################## #
# (1) OPEN CSV AND PREPARE FOR ARRAY
print("Open csv-File, format")
csv = np.genfromtxt(in_csv, delimiter = ',')
# Remove first row which are the labels in the csv, then first column which are the ID fields
csv = np.delete(csv, (0), axis=0)
csv = np.delete(csv, (0), axis=1)
# (2) CREATE OUTPUT FILES
outDrv = gdal.GetDriverByName('ENVI')
# Derive properties
nr_samples = csv.shape[0]
nr_bands = csv.shape[1] - 1
# Create file
spectra = outDrv.Create(out_spec, nr_samples, 1, nr_bands, GDT_UInt32)
labels = outDrv.Create(out_labels, nr_samples, 1, 1, GDT_Float32)

# (3) POPULATE FILES
print("Write files")
# Labels: convert into percent tree cover --> divide by 900 (pixel size of Landsat)
labs_np = csv[:,0]
labs_np = labs_np / 900
labs_out = np.expand_dims(labs_np, axis = 0)
labels.GetRasterBand(1).WriteArray(labs_out, 0, 0)
# Spectra: take values as they are --> Metrics, MetaInfo, BPC
spec_np = csv[:,1:]
spec_np = np.transpose(np.array(spec_np))
for band in range(nr_bands):
    spec_sub = spec_np[band]
    vals_out = np.expand_dims(spec_sub, axis = 0)
    spectra.GetRasterBand((band+1)).WriteArray(vals_out, 0, 0)


# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")