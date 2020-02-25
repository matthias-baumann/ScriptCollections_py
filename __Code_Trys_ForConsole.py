
# ############################################################################################################# #

# Assignment 4: Raster processing I
#
# Tillman Schmitz
#
# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import os
import gdal
import numpy as np

# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " + starttime)
print("")
# ####################################### FOLDER PATHS & global variables ##################################### #
# set working directory
os.chdir("D:/_TEACHING/__Classes-Modules_HUB/MSc-M8_Geoprocessing-with-python/Week04 - Raster Processing I/Assignment04/")

# ####################################### Exercise 1 ########################################################### #
folder = "D:/_TEACHING/__Classes-Modules_HUB/MSc-M8_Geoprocessing-with-python/Week04 - Raster Processing I/Assignment04/"
filelist = [file for file in os.listdir(folder) if file.endswith("tif")]
exit(0)
# identify maximum common extent
def overlapExtent(rasterPathlist):
    # create empty lists for the bounding coordinates and the overlap extent
    ul_x_list = []
    ul_y_list = []
    lr_x_list = []
    lr_y_list = []
    overlap_extent = []
    for path in rasterPathlist:
        raster = gdal.Open(path)

        gt = raster.GetGeoTransform() # get geo transform data
        ul_x = gt[0] # upper left x coordinate
        ul_y = gt[3] # upper left y coordinate
        lr_x = ul_x + (gt[1] * raster.RasterXSize) # upper left x coordinate + number of pixels * pixel size
        lr_y = ul_y + (gt[5] * raster.RasterYSize) # upper left y coordinate + number of pixels * pixel size
        #append bbox of every raster to the lists
        ul_x_list.append(ul_x)
        ul_y_list.append(ul_y)
        lr_x_list.append(lr_x)
        lr_y_list.append(lr_y)
    #calculate the bounding box coorinates
    overlap_extent.append(max(ul_x_list))
    overlap_extent.append(min(ul_y_list))
    overlap_extent.append(min(lr_x_list))
    overlap_extent.append(max(lr_y_list))

    return overlap_extent

print("common extent is" , overlapExtent(filelist))

img_2000 = gdal.Open(folder + "/tileID_410_y2000.tif")
img_2005 = gdal.Open(folder + "/tileID_410_y2005.tif")
img_2010 = gdal.Open(folder + "/tileID_410_y2010.tif")
img_2015 = gdal.Open(folder + "/tileID_410_y2015.tif")
img_2018 = gdal.Open(folder + "/tileID_410_y2018.tif")

imglist = [img_2000, img_2005, img_2010, img_2015, img_2018]

arrays = []
for i in imglist:

    # get geotransform information
    gt = i.GetGeoTransform()
    # invert gt because we want to o  translate  geo-coordinates  into  array-coordinates
    inv_gt = gdal.InvGeoTransform(gt)
    # apply affine transformation to get array coordinates of upperleft and lowerright corner of the common extent and change it into integer
    off_ulx, off_uly = map(int, gdal.ApplyGeoTransform(inv_gt, -63.839224823595856, -24.446662310500248))
    off_lrx, off_lry = map(int, gdal.ApplyGeoTransform(inv_gt, -63.496427711175855, -24.804012130522995))
    columns = off_lrx - off_ulx
    rows = off_lry - off_uly
    # read the common extent with transformed array coordinates into an individual array
    array =i.ReadAsArray(off_ulx, off_uly, (off_lrx - off_ulx), (off_lry - off_uly))
    arrays.append(array)

print(arrays)





