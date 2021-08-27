# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import os
import time
import math
from osgeo import ogr, gdal, osr
from osgeo.gdalconst import *
import numpy as np
import baumiTools as bt
from tqdm import tqdm
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " +  starttime)
print("")
# ####################################### DRIVERS AND FOLDER-PATHS ############################################ #
drvR = gdal.GetDriverByName('GTiff')
drvMemR = gdal.GetDriverByName('MEM')
root_folder = "L:/_SHARED_DATA/MB_TaKa/"
sa = bt.baumiVT.CopyToMem(root_folder + "India_Boundaries_CutOut.shp")
# https://spatialreference.org/ref/sr-org/south-asia-india-albers-equal-area/
out_Wkt = 'PROJCS["Albers",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Albers"],PARAMETER["standard_parallel_1",13.207886425],PARAMETER["standard_parallel_2",28.185659275],PARAMETER["latitude_of_origin",20.69677285],PARAMETER["central_meridian",82.75346985],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["Meter",1]]'
out_px = 300
# ####################################### FUNCTIONS ########################################################### #

# #### Calculate the output file properties (Extent, projection, resolution) and create the refRas
# Set the output CRS
out_SR = osr.SpatialReference()
out_SR.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
out_SR.ImportFromWkt(out_Wkt)
#out_SR.ImportFromESRI(102028)
# Get the India-Layer and convert into the new CRS, get the extent of the layer
lyr = sa.GetLayer()
ext = lyr.GetExtent()
in_SR = lyr.GetSpatialRef()
in_SR.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
tr = osr.CoordinateTransformation(in_SR, out_SR)
# Find largest extent after the coordinate transformation
ulx, uly, ulz = tr.TransformPoint(ext[0], ext[3])
llx, lly, llz = tr.TransformPoint(ext[0], ext[2])
urx, ury, ulz = tr.TransformPoint(ext[1], ext[3])
lrx, lry, llz = tr.TransformPoint(ext[1], ext[2])
minX = min(ulx, llx, urx, lrx)
maxY = max(uly, ury, lly, lry)
maxX = max(urx, lrx, ulx, llx)
minY = min(uly, lly, ury, lry)
# Calculate the new number of columns and rows
colsNew = int((maxX - minX) / out_px) + 1
rowsNew = int((maxY - minY) / out_px) + 1
originX = minX
originY = maxY
# Now create the new raster
out_gt = [originX, out_px, 0, originY, 0, -out_px]
out_pr = out_SR.ExportToWkt()
refRas = drvMemR.Create('', colsNew, rowsNew, 1, gdal.GDT_Byte)
refRas.SetProjection(out_pr)
refRas.SetGeoTransform(out_gt)
#bt.baumiRT.CopyMEMtoDisk(refRas, root_folder + "RefRas.tif")

# #### AGGREGATE HANSEN
hansen = 1
outHansen = root_folder + "Hansen_GFC-2020-v1.8/Forest2000_India_Aggregated/FC_2000-2020_India_300m.tif"
if hansen == 1:
    pass
if hansen == 0:
    print("Processing the Hansen data")
    print("--------------------------")
    windowSize = 11
# (1) Create a VRT of the Land Cover
    print("Build vrt...")
    def BuildVRT(folder, outfile):
        fileList = bt.baumiFM.GetFilesInFolderWithEnding(folder, ".tif", fullPath=True)
        vrt_options = gdal.BuildVRTOptions(resampleAlg='nearest', addAlpha=False)
        vrt = gdal.BuildVRT(outfile, fileList, options=vrt_options)
        vrt = None
        return outfile
    vrt_tc = BuildVRT(root_folder + "Hansen_GFC-2020-v1.8/Forest2000_India/", root_folder + "Hansen_GFC-2020-v1.8/Forest2000_India.vrt")
    vrt_fl = BuildVRT(root_folder + "Hansen_GFC-2020-v1.8/LossYear_India/", root_folder + "Hansen_GFC-2020-v1.8/LossYear_India.vrt")
    print("Open raster to memory")
    vrt_tc_Open = bt.baumiRT.OpenRasterToMemory(vrt_tc)#(root_folder + "Forest2000_India/20N_080E.tif")#
    vrt_fl_Open = bt.baumiRT.OpenRasterToMemory(vrt_fl)#(root_folder + "LossYear_India/20N_080E.tif")#
# (2) Get the raster information from the raster
    print("Create output-files")
    cols = vrt_tc_Open.RasterXSize
    rows = vrt_tc_Open.RasterYSize
    gt = vrt_tc_Open.GetGeoTransform()
    pr = vrt_tc_Open.GetProjection()
# (3) build the output-file
    cols = windowSize * (math.floor(cols / windowSize))
    rows = windowSize * (math.floor(rows / windowSize))
    outCols = int(cols / windowSize)
    outRows = int(rows / windowSize)
    cols = cols - 1
    rows = rows - 1
    out_gt = [gt[0], float(gt[1])*windowSize, gt[2], gt[3], gt[4], float(gt[5])*windowSize] # Build new GeoTransform
    out = drvMemR.Create('', outCols, outRows, 1, GDT_Float32)
    out.SetProjection(pr)
    out.SetGeoTransform(out_gt)
# (4) Instantiate output array
    wl = np.zeros((outRows, outCols, 21), dtype=np.float)
# (5) Start the loop
    print("Do the aggregation")
    time.sleep(1)
    out_i = 0
    for i in tqdm(range(0, cols, windowSize)):
        if i + windowSize < cols:
            numCols = windowSize
        else:
            numCols = cols - i
        out_j = 0
        for j in range(0, rows, windowSize):
            if j + windowSize < rows:
                numRows = windowSize
            else:
                numRows = rows - j
# (6) Do the operation inside the loop
        # Load the arrays
            tc_in = vrt_tc_Open.GetRasterBand(1).ReadAsArray(i, j, numCols, numRows)
            fl_in = vrt_fl_Open.GetRasterBand(1).ReadAsArray(i, j, numCols, numRows)
        # Forest in 2000
            tc_in_bin = np.where(tc_in > 5, 1, 0)
            tc_p = tc_in_bin.sum()
            wl[out_j, out_i, 0] = tc_p
            testList = [tc_p]
        # Now loss per year
            for value in range(1, 20+1):
                # Calculate the proportions
                #tc_in_bin_fl = np.where(np.logical_and(fl_in <= value, tc_in_bin==1, fl_in > 0), 0, tc_in_bin)
                tc_in_bin = np.where(fl_in == value, 0, tc_in_bin)
                tc_p_y = tc_in_bin.sum()
                testList.append(tc_p_y)
                wl[out_j, out_i, value] = tc_p_y
            # Increase counter
            out_j += 1
        out_i += 1
# (7) Create virtual rasters in memory for each land cover
    print("Create virtual raster files")
    def CreateMEMRas(arr, cols, rows, gt, pr, type):
        # Get numbber of bands from array (i.e. third dimension
        dims = arr.ndim
        if dims == 2:
            outRas = drvMemR.Create('', cols, rows, 1, type)
            outRas.SetProjection(pr)
            outRas.SetGeoTransform(gt)
            outRas.GetRasterBand(1).WriteArray(arr, 0, 0)
        if dims > 2:
            outRas = drvMemR.Create('', cols, rows, arr.shape[2], type)
            outRas.SetProjection(pr)
            outRas.SetGeoTransform(gt)
            for bandCount, arrCount in enumerate(range(arr.shape[2]), start=1):
                outRas.GetRasterBand(bandCount).WriteArray(arr[:, :, arrCount], 0, 0)
        return outRas
    wl_ras = CreateMEMRas(wl, outCols, outRows, out_gt, pr, GDT_UInt16)
# (8) Write to disc
    print("Write to disc")
    bt.baumiRT.CopyMEMtoDisk(wl_ras, outHansen)
# (9) Add band names
    # Rename the band names
    final_open = gdal.Open(outHansen)
    for band, year in enumerate(range(2000, 2020 + 1), start=1):
        rb = final_open.GetRasterBand(band)
        rb_name = "TC_" + str(year) + "_300m"
        rb.SetDescription(rb_name)

# RESAMPLE MODIS TO HANSEN
modis = 1
outMODIS = root_folder + "MODIS_2000-2020/MODIS_PNTV_2000-2020_India_300m_trimmed.tif"
if modis == 1:
    pass
if modis == 0:
    # Create a new file in memory
    outFile = drvMemR.Create('', colsNew, rowsNew, 21, gdal.GDT_UInt16)
    outFile.SetProjection(out_pr)
    outFile.SetGeoTransform(out_gt)

    # Define the input file for the individual raster files
    inFolder = root_folder + "MODIS_2000-2020/RAW DATA/"
    # Loop over the individual years
    for band, yr in enumerate(range(2000, 2020+1, 1), start=1):
        # Build a vrt of the files of that respective year
        files = [inFolder + file for file in os.listdir(inFolder) if file.find(str(yr)) >= 0 and file.endswith(".hdf")]
        subFiles = []
        for file in files:
            dataset = gdal.Open(file, GA_ReadOnly)
            subdatasets = dataset.GetSubDatasets()
            subFiles.append(subdatasets[1][0])

        vrt_name = root_folder + "MODIS_2000-2020/VRT-tmp_" + str(yr) + ".vrt"
        vrt_options = gdal.BuildVRTOptions(resampleAlg='nearest', addAlpha=False)
        gdal.BuildVRT(vrt_name, subFiles, options=vrt_options)
        vrt_open = gdal.Open(vrt_name)
        # Now reproject it into the first band of the new file
        tmp_ds = drvMemR.Create('', colsNew, rowsNew, 1, gdal.GDT_UInt16)
        tmp_ds.SetProjection(out_pr)
        tmp_ds.SetGeoTransform(out_gt)
        warp_options = gdal.WarpOptions(outputType=gdal.GDT_UInt16, xRes=out_px, yRes=out_px,
                                        srcSRS=vrt_open.GetProjection(), dstSRS=out_pr,
                                        resampleAlg='bilinear')
        gdal.Warp(destNameOrDestDS=tmp_ds, srcDSOrSrcDSTab=vrt_open, options=warp_options)
        # Mask out non TC values
        tmp_arr = tmp_ds.GetRasterBand(1).ReadAsArray()
        tmp_arr = np.where(tmp_arr > 100, 0, tmp_arr)
        outFile.GetRasterBand(band).WriteArray(tmp_arr, 0, 0)
        # Delete the temporary file and the vrt
        tmp_ds = None
        vrt_open = None
        os.remove(vrt_name)
    # Test: write to disc
        #tmp_ds.GetRasterBand(band).WriteArray(tmp_arr, 0, 0)
        #bt.baumiRT.CopyMEMtoDisk(tmp_ds, root_folder + "MODIS_2000-2020/MODIS_TC_2000-TEST_India_300m.tif")
        #outFile = bt.baumiRT.OpenRasterToMemory(root_folder + "MODIS_2000-2020/MODIS_TC_2000-TEST_India_300m.tif")
        #exit(0)
    outDS_trim = bt.baumiRT.ClipRasterBySHP(sa, outFile, mask=True)
    bt.baumiRT.CopyMEMtoDisk(outDS_trim, outMODIS)
    # Rename the bands
    final_open = gdal.Open(outMODIS)
    for band, year in enumerate(range(2000, 2020+1), start=1):
        rb = final_open.GetRasterBand(band)
        rb_name = "MODIS_PNTV_" + str(year) + "_300m"
        rb.SetDescription(rb_name)

# #### MATCH ROY TO HANSEN
roy = 1
outRoy = root_folder + "Roy/FC_1985-1995-2005_India_300m_trimmed.tif"
if roy == 1:
    pass
if roy == 0:
    print("Processing the Roy data")
    print("-----------------------")
    classConv = [1, 4, 5, 8, 10, 12, 15, 16, 17, 19]
# Path to the three files
    f85 = root_folder + "Roy/LULC_1985/fin_ind_85.img"
    f95 = root_folder + "Roy/LULC_1995/fin_ind_95.img"
    f05 = root_folder + "Roy/LULC_2005/fin_ind_05.img"
# Reclassify the files
    print("Reclassifying")
    def Reclassify(inPath, printYear):
    # Open the raster get the properties
        print("Year:", str(printYear))
        ds = gdal.Open(inPath)
        cols = ds.RasterXSize
        rows = ds.RasterYSize
        pr = ds.GetProjection()
        gt = ds.GetGeoTransform()
    # Create a new file in memory
        out_ds = drvMemR.Create('', cols, rows, 1, GDT_Byte)
        out_ds.SetProjection(pr)
        out_ds.SetGeoTransform(gt)
    # Loop over the rows
        for row in tqdm(range(rows)):
            in_arr = ds.GetRasterBand(1).ReadAsArray(0, row, cols, 1)
            out_arr = np.zeros_like(in_arr)
        # Re-Classify into binary cover based on the rulesets
            for c in classConv:
                out_arr = np.where(in_arr == c, 1, out_arr)
        # Write to output file
            out_ds.GetRasterBand(1).WriteArray(out_arr, 0, row)
    # return output file
        return out_ds
    f85_bin = Reclassify(f85, 1985)
    #bt.baumiRT.CopyMEMtoDisk(f85_bin, outRoy)
    #exit(0)
    f95_bin = Reclassify(f95, 1995)
    f05_bin = Reclassify(f05, 2005)
    print("")
# Open the Hansen data, to get the properties
    refCols = refRas.RasterXSize
    refRows = refRas.RasterYSize
    refPR = refRas.GetProjection()
    refGT = refRas.GetGeoTransform()
    pxSize = refGT[1]
# Reproject the files into the new raster
    print("Reprojecting")
    def Reproject_roy(inFile, cl, rw, proj, geotr, printYear):
        print("Year:", str(printYear))
        in_pr = inFile.GetProjection()
    # Build the new file in memory
        out_file = drvMemR.Create('', cl, rw, 1, GDT_Byte)
        out_file.SetProjection(proj)
        out_file.SetGeoTransform(geotr)
    # Apply the warping
        warp_options = gdal.WarpOptions(outputType=gdal.GDT_Byte, xRes=pxSize, yRes=pxSize,
                                        srcSRS=in_pr, dstSRS=proj, resampleAlg='sum')
        gdal.Warp(destNameOrDestDS=out_file, srcDSOrSrcDSTab=inFile, options=warp_options)
    # Apply conversion factor to account for percentages based on the spatial resolution
        in_arr = out_file.GetRasterBand(1).ReadAsArray(0, 0, cl, rw)
        max = np.amax(in_arr)
        in_arr = (in_arr / max * 100).astype(int)
        out_file.GetRasterBand(1).WriteArray(in_arr, 0, 0)
    # return the output-file
        return out_file
    f85_reproj = Reproject_roy(f85_bin, refCols, refRows, refPR, refGT, 1985)
    #bt.baumiRT.CopyMEMtoDisk(f85_reproj, outRoy)
    #exit(0)
    f95_reproj = Reproject_roy(f95_bin, refCols, refRows, refPR, refGT, 1995)
    f05_reproj = Reproject_roy(f05_bin, refCols, refRows, refPR, refGT, 2005)
    print("Merge the three")
# Merge the three files into one single file, which will be the output
    outDS = drvMemR.Create('', refCols, refRows, 3, GDT_Byte)
    outDS.SetProjection(refPR)
    outDS.SetGeoTransform(refGT)
    outDS.GetRasterBand(1).WriteArray(f85_reproj.GetRasterBand(1).ReadAsArray(0, 0, refCols, refRows), 0, 0)
    outDS.GetRasterBand(2).WriteArray(f95_reproj.GetRasterBand(1).ReadAsArray(0, 0, refCols, refRows), 0, 0)
    outDS.GetRasterBand(3).WriteArray(f05_reproj.GetRasterBand(1).ReadAsArray(0, 0, refCols, refRows), 0, 0)
# Trim the data by the study region shape
    outDS_trim = bt.baumiRT.ClipRasterBySHP(sa, outDS, mask=True)
    bt.baumiRT.CopyMEMtoDisk(outDS_trim, outRoy)
# Rename the bands
    final_open = gdal.Open(outRoy)
    for band, year in enumerate([1985, 1995, 2005], start=1):
        rb = final_open.GetRasterBand(band)
        rb_name = "Roy_TC_" + str(year) + "_300m"
        rb.SetDescription(rb_name)

# MATCH THE MOULDS TO HANSEN
moulds = 1
outMoulds = root_folder + "Moulds_1960/FC_1960-2020_India_300m_trimmed.tif"
if moulds == 1:
    pass
if moulds == 0:
    print("Processing the Moulds data")
    print("-----------------------")
    classConv = [2, 4]
    # Path to the three files
    f60 = root_folder + "Moulds_1960/Raw/INDIA_LULC_MOD_1960.tif"
    f70 = root_folder + "Moulds_1960/Raw/INDIA_LULC_MOD_1970.tif"
    f80 = root_folder + "Moulds_1960/Raw/INDIA_LULC_MOD_1980.tif"
    f90 = root_folder + "Moulds_1960/Raw/INDIA_LULC_MOD_1990.tif"
    f00 = root_folder + "Moulds_1960/Raw/INDIA_LULC_MOD_2000.tif"
    f10 = root_folder + "Moulds_1960/Raw/INDIA_LULC_MOD_2010.tif"
    # Reclassify the files
    print("Reclassifying")
    def Reclassify(inPath, printYear):
        # Open the raster get the properties
        print("Year:", str(printYear))
        ds = gdal.Open(inPath)
        cols = ds.RasterXSize
        rows = ds.RasterYSize
        pr = ds.GetProjection()
        gt = ds.GetGeoTransform()
        # Create a new file in memory
        out_ds = drvMemR.Create('', cols, rows, 1, GDT_Byte)
        out_ds.SetProjection(pr)
        out_ds.SetGeoTransform(gt)
        # Loop over the rows
        for row in tqdm(range(rows)):
            in_arr = ds.GetRasterBand(1).ReadAsArray(0, row, cols, 1)
            out_arr = np.zeros_like(in_arr)
            # Re-Classify into binary cover based on the rulesets
            for c in classConv:
                out_arr = np.where(in_arr == c, 1, out_arr)
            # Write to output file
            out_ds.GetRasterBand(1).WriteArray(out_arr, 0, row)
        # return output file
        return out_ds
    f60_bin = Reclassify(f60, 1960)
    #bt.baumiRT.CopyMEMtoDisk(f60_bin, outMoulds)
    #exit(0)
    f70_bin = Reclassify(f70, 1970)
    f80_bin = Reclassify(f80, 1980)
    f90_bin = Reclassify(f90, 1990)
    f00_bin = Reclassify(f00, 2000)
    f10_bin = Reclassify(f10, 2010)

    # Open the Hansen data, to get the properties
    refCols = refRas.RasterXSize
    refRows = refRas.RasterYSize
    refPR = refRas.GetProjection()
    refGT = refRas.GetGeoTransform()
    pxSize = refGT[1]
    # Reproject the files into the new raster
    print("Reprojecting")
    def Reproject_moulds(inFile, cl, rw, proj, geotr, printYear):
        print("Year:", str(printYear))
        in_pr = inFile.GetProjection()
        # Build the new file in memory
        out_file = drvMemR.Create('', cl, rw, 1, GDT_Byte)
        out_file.SetProjection(proj)
        out_file.SetGeoTransform(geotr)
        # Apply the warping
        warp_options = gdal.WarpOptions(outputType=gdal.GDT_Byte, xRes=pxSize, yRes=pxSize,
                                        srcSRS=in_pr, dstSRS=proj, resampleAlg='sum')
        gdal.Warp(destNameOrDestDS=out_file, srcDSOrSrcDSTab=inFile, options=warp_options)
        # Apply conversion factor to account for percentages based on the spatial resolution
        # --> from try-Out: 100% TC has sum of 8
        in_arr = out_file.GetRasterBand(1).ReadAsArray(0, 0, cl, rw)
        max = np.amax(in_arr)
        in_arr = (in_arr / max * 100).astype(int)
        #for r in range(rw):
        #    in_arr = out_file.GetRasterBand(1).ReadAsArray(0, r, cl, 1)
        #    in_arr = (in_arr / 8 * 100).astype(int)
        #    out_file.GetRasterBand(1).WriteArray(in_arr, 0, r)
        out_file.GetRasterBand(1).WriteArray(in_arr, 0, 0)
        # return the output-file
        return out_file
    f60_reproj = Reproject_moulds(f60_bin, refCols, refRows, refPR, refGT, 1960)
    #bt.baumiRT.CopyMEMtoDisk(f60_reproj, outMoulds)
    #exit(0)
    f70_reproj = Reproject_moulds(f70_bin, refCols, refRows, refPR, refGT, 1970)
    f80_reproj = Reproject_moulds(f80_bin, refCols, refRows, refPR, refGT, 1980)
    f90_reproj = Reproject_moulds(f90_bin, refCols, refRows, refPR, refGT, 1990)
    f00_reproj = Reproject_moulds(f00_bin, refCols, refRows, refPR, refGT, 2000)
    f10_reproj = Reproject_moulds(f10_bin, refCols, refRows, refPR, refGT, 2010)
    print("Merge the six")
    # Merge the three files into one single file, which will be the output
    outDS = drvMemR.Create('', refCols, refRows, 6, GDT_Byte)
    outDS.SetProjection(refPR)
    outDS.SetGeoTransform(refGT)
    outDS.GetRasterBand(1).WriteArray(f60_reproj.GetRasterBand(1).ReadAsArray(0, 0, refCols, refRows), 0, 0)
    outDS.GetRasterBand(2).WriteArray(f70_reproj.GetRasterBand(1).ReadAsArray(0, 0, refCols, refRows), 0, 0)
    outDS.GetRasterBand(3).WriteArray(f80_reproj.GetRasterBand(1).ReadAsArray(0, 0, refCols, refRows), 0, 0)
    outDS.GetRasterBand(4).WriteArray(f90_reproj.GetRasterBand(1).ReadAsArray(0, 0, refCols, refRows), 0, 0)
    outDS.GetRasterBand(5).WriteArray(f00_reproj.GetRasterBand(1).ReadAsArray(0, 0, refCols, refRows), 0, 0)
    outDS.GetRasterBand(6).WriteArray(f10_reproj.GetRasterBand(1).ReadAsArray(0, 0, refCols, refRows), 0, 0)
    # Trim the data
    outDS_trim = bt.baumiRT.ClipRasterBySHP(sa, outDS, mask=True)
    bt.baumiRT.CopyMEMtoDisk(outDS_trim, outMoulds)
    # Rename the bands
    final_open = gdal.Open(outMoulds)
    for band, year in enumerate([1960, 1970, 1980, 1990, 2000, 2010], start=1):
        rb = final_open.GetRasterBand(band)
        rb_name = "Moulds_TC_" + str(year) + "_300m"
        rb.SetDescription(rb_name)



# CREATE A CONSISTENT TIME SERIES
consistency = 0
outCons = root_folder + "TimeSeries_Moulds-Hansen.tif"
if consistency == 1:
    pass
if consistency == 0:
    print("Creating a consistent time series")
    print("-----------------------")
    hans = gdal.Open(outHansen)
    moulds = gdal.Open(outRoy)
    # (1) Get the raster information from the raster
    print("Create output-files")
    cols = hans.RasterXSize
    rows = hans.RasterYSize
    gt = hans.GetGeoTransform()
    pr = hans.GetProjection()
    # (2) Create the output-File
    outDS = drvMemR.Create('', refCols, refRows, 24, GDT_Byte)
    outDS.SetProjection(pr)
    outDS.SetGeoTransform(gt)
    # (3) Populate the bands 5-24 with the hansen data
    for outBand, inBand in enumerate(range(1, 20+1), start=5):
        # Do the processing row-wise to
        for row in tqdm(range(rows)):
            in_arr = hans.GetRasterBand(inBand).ReadAsArray(0, row, cols, 1)
            outDS.GetRasterBand(outBand).WriteArray(in_arr, 0, row)
    # (4) Populate the bands 1-4 with the mMoulds data, check for consistency





# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")