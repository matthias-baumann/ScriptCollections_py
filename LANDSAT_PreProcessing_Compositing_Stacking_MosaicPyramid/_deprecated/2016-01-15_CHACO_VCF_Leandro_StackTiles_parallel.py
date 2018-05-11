# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import os
import time
import gdal
from gdalconst import *
from multiprocessing import Pool

def main():
    # ####################################### SET TIME-COUNT ###################################################### #
    starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print("--------------------------------------------------------")
    print("Starting process, time:" + starttime)
    print("")
    # ####################################### FUNCTIONS, FOLDER PATHS AND BASIC VARIABLES ######################### #
    img_folder = "E:/Baumann/CHACO/_Composite_Landsat8_2015/DOY015_Jan15/"
    meta_folder = "E:/Baumann/CHACO/_Composite_Landsat8_2015/DOY015_Jan15_MetaInfo/"
    metrics_folder = "E:/Baumann/CHACO/_Composite_Landsat8_2015/Metrics_Nov15/"
    # ####################################### PROCESSING ########################################################## #
    # (1) GET LISTS OF TILES FOR THE YEARS WE WANT TO STACK
    imgList = [file for file in os.listdir(img_folder) if file.endswith("Imagery.bsq")]
    #imgList = imgList[1999:2000]
    stackLists = []
    for img in imgList:
        list = []
        # DOY015 - bands
        image = img_folder + img
        list.append(image)
        # DOY015 - flags
        metaInfo = meta_folder + img
        metaInfo = metaInfo.replace("Imagery.bsq","MetaFlags.bsq")
        list.append(metaInfo)
        # DOY074 - bands
        img_folder_u = img_folder
        img_folder_u = img_folder_u.replace("DOY015_Jan15", "DOY074_Mar15")
        image = img_folder_u + img
        list.append(image)
        # DOY074 - flags
        meta_folder_u = meta_folder
        meta_folder_u = meta_folder_u.replace("DOY015_Jan15_MetaInfo", "DOY074_Mar15_MetaInfo")
        metaInfo = meta_folder_u + img
        metaInfo = metaInfo.replace("Imagery.bsq","MetaFlags.bsq")
        list.append(metaInfo)
        # DOY135 - bands
        img_folder_u = img_folder
        img_folder_u = img_folder_u.replace("DOY015_Jan15", "DOY135_May15")
        image = img_folder_u + img
        list.append(image)
        # DOY135 - flags
        meta_folder_u = meta_folder
        meta_folder_u = meta_folder_u.replace("DOY015_Jan15_MetaInfo", "DOY135_May15_MetaInfo")
        metaInfo = meta_folder_u + img
        metaInfo = metaInfo.replace("Imagery.bsq","MetaFlags.bsq")
        list.append(metaInfo)
        # DOY196 - bands
        img_folder_u = img_folder
        img_folder_u = img_folder_u.replace("DOY015_Jan15", "DOY196_Jul15")
        image = img_folder_u + img
        list.append(image)
        # DOY196 - flags
        meta_folder_u = meta_folder
        meta_folder_u = meta_folder_u.replace("DOY015_Jan15_MetaInfo", "DOY196_Jul15_MetaInfo")
        metaInfo = meta_folder_u + img
        metaInfo = metaInfo.replace("Imagery.bsq","MetaFlags.bsq")
        list.append(metaInfo)
        # DOY258 - bands
        img_folder_u = img_folder
        img_folder_u = img_folder_u.replace("DOY015_Jan15", "DOY258_Sep15")
        image = img_folder_u + img
        list.append(image)
        # DOY258 - flags
        meta_folder_u = meta_folder
        meta_folder_u = meta_folder_u.replace("DOY015_Jan15_MetaInfo", "DOY258_Sep15_MetaInfo")
        metaInfo = meta_folder_u + img
        metaInfo = metaInfo.replace("Imagery.bsq","MetaFlags.bsq")
        list.append(metaInfo)
        # DOY319 - bands
        img_folder_u = img_folder
        img_folder_u = img_folder_u.replace("DOY015_Jan15", "DOY319_Nov15")
        image = img_folder_u + img
        list.append(image)
        # DOY319 - flags
        meta_folder_u = meta_folder
        meta_folder_u = meta_folder_u.replace("DOY015_Jan15_MetaInfo", "DOY319_Nov15_MetaInfo")
        metaInfo = meta_folder_u + img
        metaInfo = metaInfo.replace("Imagery.bsq","MetaFlags.bsq")
        list.append(metaInfo)
        # Metrics
        metric = metrics_folder + img
        metric = metric.replace("Imagery.bsq","Metrics.bsq")
        list.append(metric)
        # Append
        stackLists.append(list)
    pool = Pool(processes=20)
    pool.map(WorkerFunction, stackLists)
    pool.close()
    pool.join()
    # ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
    print("")
    endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print("--------------------------------------------------------")
    print("--------------------------------------------------------")
    print("start: " + starttime)
    print("end: " + endtime)
    print("")


def WorkerFunction(stackLists):
    # ####################################### FUNCTIONS, FOLDER PATHS AND BASIC VARIABLES ######################### #
    out_folder = "L:/biogeo-lab/SAN_BioGeo/_SHARED_DATA/CL_MB/_00_ls_data_stacks/"
    outext = "StackAll"
    drvMemR = gdal.GetDriverByName('MEM')
    drvR = gdal.GetDriverByName('ENVI')
    bflags = [6, 8, 9]
    outbands = 117
    # ####################################### PROCESSING ########################################################## #
    stack = stackLists
    # Build output filename
    p = stack[0].rfind("/")
    file = stack[0][p+1:]
    file = file.replace("PBC_multiYear_Imagery", outext)
    outfile = out_folder + file
    print("Processing: " + outfile)
    # Load files into memory, get properties
    doy015_img = drvMemR.CreateCopy('', gdal.Open(stack[0]))
    doy015_flag = drvMemR.CreateCopy('', gdal.Open(stack[1]))
    doy074_img = drvMemR.CreateCopy('', gdal.Open(stack[2]))
    doy074_flag = drvMemR.CreateCopy('', gdal.Open(stack[3]))
    doy135_img = drvMemR.CreateCopy('', gdal.Open(stack[4]))
    doy135_flag = drvMemR.CreateCopy('', gdal.Open(stack[5]))
    doy196_img = drvMemR.CreateCopy('', gdal.Open(stack[6]))
    doy196_flag = drvMemR.CreateCopy('', gdal.Open(stack[7]))
    doy258_img = drvMemR.CreateCopy('', gdal.Open(stack[8]))
    doy258_flag = drvMemR.CreateCopy('', gdal.Open(stack[9]))
    doy319_img = drvMemR.CreateCopy('', gdal.Open(stack[10]))
    doy319_flag = drvMemR.CreateCopy('', gdal.Open(stack[11]))
    metric = drvMemR.CreateCopy('', gdal.Open(stack[12]))
    cols = metric.RasterXSize
    rows = metric.RasterYSize
    proj = metric.GetProjection()
    geotrans = metric.GetGeoTransform()
    bands = outbands
    # Create Output tile
    out = drvMemR.Create('', cols, rows, bands, GDT_UInt32)
    out.SetProjection(proj)
    out.SetGeoTransform(geotrans)
    # Populate output file
    b = 1
    # DOY 015
    for b_in in range(doy015_img.RasterCount):
        readOut = doy015_img.GetRasterBand(b_in+1).ReadAsArray(0, 0, cols, rows)
        out.GetRasterBand(b).WriteArray(readOut)
        b = b+1
    for b_in in bflags:
        readOut = doy015_flag.GetRasterBand(b_in).ReadAsArray(0, 0, cols, rows)
        out.GetRasterBand(b).WriteArray(readOut)
        b = b+1
    # DOY 074
    for b_in in range(doy074_img.RasterCount):
        readOut = doy074_img.GetRasterBand(b_in+1).ReadAsArray(0, 0, cols, rows)
        out.GetRasterBand(b).WriteArray(readOut)
        b = b+1
    for b_in in bflags:
        readOut = doy074_flag.GetRasterBand(b_in).ReadAsArray(0, 0, cols, rows)
        out.GetRasterBand(b).WriteArray(readOut)
        b = b+1
    # DOY 135
    for b_in in range(doy135_img.RasterCount):
        readOut = doy135_img.GetRasterBand(b_in+1).ReadAsArray(0, 0, cols, rows)
        out.GetRasterBand(b).WriteArray(readOut)
        b = b+1
    for b_in in bflags:
        readOut = doy135_flag.GetRasterBand(b_in).ReadAsArray(0, 0, cols, rows)
        out.GetRasterBand(b).WriteArray(readOut)
        b = b+1
    # DOY 196
    for b_in in range(doy196_img.RasterCount):
        readOut = doy196_img.GetRasterBand(b_in+1).ReadAsArray(0, 0, cols, rows)
        out.GetRasterBand(b).WriteArray(readOut)
        b = b+1
    for b_in in bflags:
        readOut = doy196_flag.GetRasterBand(b_in).ReadAsArray(0, 0, cols, rows)
        out.GetRasterBand(b).WriteArray(readOut)
        b = b+1
    # DOY 258
    for b_in in range(doy258_img.RasterCount):
        readOut = doy258_img.GetRasterBand(b_in+1).ReadAsArray(0, 0, cols, rows)
        out.GetRasterBand(b).WriteArray(readOut)
        b = b+1
    for b_in in bflags:
        readOut = doy258_flag.GetRasterBand(b_in).ReadAsArray(0, 0, cols, rows)
        out.GetRasterBand(b).WriteArray(readOut)
        b = b+1
    # DOY 319
    for b_in in range(doy319_img.RasterCount):
        readOut = doy319_img.GetRasterBand(b_in+1).ReadAsArray(0, 0, cols, rows)
        out.GetRasterBand(b).WriteArray(readOut)
        b = b+1
    for b_in in bflags:
        readOut = doy319_flag.GetRasterBand(b_in).ReadAsArray(0, 0, cols, rows)
        out.GetRasterBand(b).WriteArray(readOut)
        b = b+1
    # Metrics
    for b_in in range(metric.RasterCount):
        readOut = metric.GetRasterBand(b_in+1).ReadAsArray(0, 0, cols, rows)
        out.GetRasterBand(b).WriteArray(readOut)
        b = b+1
    # Now the last three bands of the DOY015 file for the R-code from Christian
    for b_in in [3, 8, 9]:
        readOut = doy015_flag.GetRasterBand(b_in).ReadAsArray(0, 0, cols, rows)
        out.GetRasterBand(b).WriteArray(readOut)
        b = b+1
# (3) COPY OUTPUT TO DISK
    drvR.CreateCopy(outfile, out)
if __name__ == "__main__":
    main()
