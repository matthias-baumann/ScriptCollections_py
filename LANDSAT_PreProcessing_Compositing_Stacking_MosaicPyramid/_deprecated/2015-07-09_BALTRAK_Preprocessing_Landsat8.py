# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import os
import time
import xml.etree.ElementTree as ET
import tarfile
import gdal, osr, ogr
from gdalconst import *
import numpy as np
import shutil
from multiprocessing import Pool
from ZumbaTools.Raster_Tools import *
import gzip
# ############################################################################################################# #
def main():
# ####################################### SET TIME-COUNT ###################################################### #
    starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print("--------------------------------------------------------")
    print("Starting process, time:" +  starttime)
    print("")
# ####################################### FOOTPRINTS ########################################################## #
# (1) GET LIST OF SCENES TO BE PROCESSED
    in_root = "H:/Baltrak/01_PreProcessing/04_Landsat8_SR_RAW/"
    scene_list = [input for input in os.listdir(in_root) if input.endswith('.tar.gz')]

    pool = Pool(processes=24)
    pool. map(WorkerFunction, scene_list)
    pool.close()
    pool.join()
# ####################################### END TIME-COUNT AND PRINT TIME STATS ################################# #
    print("")
    endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print("--------------------------------------------------------")
    print("--------------------------------------------------------")
    print("start: ", starttime)
    print("end: ", endtime)
    print("")

def WorkerFunction(scenes):
# ####################################### GLOBAL FUNCTIONS #################################################### #
    def unzip(filePath):
        # Create output-path
        outpath = filePath
        outpath = outpath.replace(".tar.gz", "")
        if not os.path.exists(outpath):
            try:
                os.makedirs(outpath)
            except:
                print("Folder already exists...")
        tar = tarfile.open(filePath, "r")
        list = tar.getnames()
        for file in tar:
            tar.extract(file, outpath)
        tar.close()
        # Rename folder where files are in, so that it gets the sceneID-name
        mtl = [file for file in os.listdir(outpath) if file.endswith("_MTL.txt")]
        archivename = mtl[0]
        archivename = archivename[:-8]
        old_foldername = outpath
        p = outpath.rfind("/")
        new_foldername = outpath[:p + 1] + archivename
        os.rename(old_foldername, new_foldername)
        new_foldername = new_foldername + "/"
        return new_foldername
    def Ctrans_MEM(inband_MEM, file_t_srs):
        # Function to convert into new coordinate system, for instructions, see http://jgomezdans.github.io/gdal_notes/reprojection.html
        # (1) Define projection rule for output-projection
        # (1-1) Get properties from input-band
        cols = inband_MEM.RasterXSize
        rows = inband_MEM.RasterYSize
        in_proj = inband_MEM.GetProjection()
        in_geotrans = inband_MEM.GetGeoTransform()
        in_datatype = inband_MEM.GetRasterBand(1).DataType
        # (1-2) Get properties of projection to be projected into --> comes from file_t_srs
        s_srs_raster = gdal.Open(file_t_srs, GA_ReadOnly)
        out_proj = s_srs_raster.GetProjection()
        # (1-3) Build the coordinate transformation
        source_SR = osr.SpatialReference()
        source_SR.ImportFromWkt(in_proj)
        target_SR = osr.SpatialReference()
        target_SR.ImportFromWkt(out_proj)
        transgeo = osr.CoordinateTransformation(source_SR, target_SR)
        # (1-4) GET ALL FOUR CORNER COORDINATES OF THE IMAGE, transform, make largest new extent
        cornercords = GetExtent(inband_MEM)
        cornercords_t = TransformCorners(cornercords, transgeo)
        UL = [min([x[0] for x in cornercords_t]),max([x[1] for x in cornercords_t])]
        LR = [max([x[0] for x in cornercords_t]),min([x[1] for x in cornercords_t])]
        # (2-1) Generate new GeoTrans
        out_geotrans = (UL[0], 30.0, in_geotrans[2], UL[1], in_geotrans[4], -30.0)
        # (2-2) Update Number of cols and rows, which may be different after the coordinate transformation
        new_cols = int((LR[0] - UL[0]) / 30.0)
        new_rows = int((UL[1] - LR[1]) / 30.0)
        # (3) Generate output-file, and do the transformation
        out_MEM = drvMemR.Create('', new_cols, new_rows, 1, in_datatype)
        out_MEM.SetProjection(out_proj)
        out_MEM.SetGeoTransform(out_geotrans)
        res = gdal.ReprojectImage(inband_MEM, out_MEM, source_SR.ExportToWkt(), target_SR.ExportToWkt(),
                                  gdal.GRA_NearestNeighbour)
        return out_MEM
    def GetExtent(inband_MEM):
        # Get geotransform, get cols, get rows
        gt = inband_MEM.GetGeoTransform()
        cols = inband_MEM.RasterXSize
        rows = inband_MEM.RasterYSize
        # Get extent from gt und cols,rows.
        # found at http://gis.stackexchange.com/questions/57834/how-to-get-raster-corner-coordinates-using-python-gdal-bindings
        # Format is: [[UpperLeft],[LowerLeft],[LowerRight],[UpperRight]]
        ext=[]
        xarr=[0,cols]
        yarr=[0,rows]
        for px in xarr:
            for py in yarr:
                x=gt[0]+(px*gt[1])+(py*gt[2])
                y=gt[3]+(px*gt[4])+(py*gt[5])
                ext.append([x,y])
            yarr.reverse()
        return ext
    def TransformCorners(extent, transformation):
        extent_transform = []
        for corner in extent:
            (x, y, z) = transformation.TransformPoint(corner[0], corner[1])
            corner_t = [x,y]
            extent_transform.append(corner_t)
        return extent_transform
# ####################################### GLOBAL PATHS ######################################################## #
    in_root = "H:/Baltrak/01_PreProcessing/04_Landsat8_SR_RAW/"
    out_root = "H:/Baltrak/01_PreProcessing/02_ReProjected_Scenes_L8/"
    raster_for_projection = "H:/Baltrak/03_Classification/Run02_Classification"
# ####################################### START PROCESSING #################################################### #
    item = scenes
    print("Processing Scene: " + item)
    # ### (0) CREATE FOLDER STRUCTURE
    # Create input-Path
    in_path = in_root + item
    # Create output-Path
    PR = item[3:6] + "_" + item[6:9]
    out_folder = out_root + PR + "/"
    if not os.path.exists(out_folder):
        try:
            os.makedirs(out_folder)
        except:
            print("Folder already exists")
    target_path = out_folder + item
    # move file
    shutil.copy(in_path, target_path)
    # #### (1) UNZIP THE ARCHIVE
    print("Unzipping, " + item)
    new_targetPath = unzip(target_path)
    # #### (2) LOAD THE INPUT-RASTER INTO MEMORY
    print("Load files into memory, " + item)
    drvMemR = gdal.GetDriverByName('MEM')
    scenePath = new_targetPath
    b10 = drvMemR.CreateCopy('',gdal.Open(scenePath + "/" + [file for file in os.listdir(scenePath) if file.endswith('band10.tif')][0]))
    b2 = drvMemR.CreateCopy('', gdal.Open(scenePath + "/" + [file for file in os.listdir(scenePath) if file.endswith('band2.tif')][0]))
    b3 = drvMemR.CreateCopy('', gdal.Open(scenePath + "/" + [file for file in os.listdir(scenePath) if file.endswith('band3.tif')][0]))
    b4 = drvMemR.CreateCopy('', gdal.Open(scenePath + "/" + [file for file in os.listdir(scenePath) if file.endswith('band4.tif')][0]))
    b5 = drvMemR.CreateCopy('', gdal.Open(scenePath + "/" + [file for file in os.listdir(scenePath) if file.endswith('band5.tif')][0]))
    b6 = drvMemR.CreateCopy('', gdal.Open(scenePath + "/" + [file for file in os.listdir(scenePath) if file.endswith('band6.tif')][0]))
    b7 = drvMemR.CreateCopy('', gdal.Open(scenePath + "/" + [file for file in os.listdir(scenePath) if file.endswith('band7.tif')][0]))
    cf = drvMemR.CreateCopy('', gdal.Open(scenePath + "/" + [file for file in os.listdir(scenePath) if file.endswith('cfmask.tif')][0]))
    # #### (3) START THE PROCESSING
    # #### (3-1) GEO-TRANsFORM THE BANDS IN MEMORY
    print("Coordinate Transformation, " + item)
    b10_trans = Ctrans_MEM(b10, raster_for_projection)
    b2_trans = Ctrans_MEM(b2, raster_for_projection)
    b3_trans = Ctrans_MEM(b3, raster_for_projection)
    b4_trans = Ctrans_MEM(b4, raster_for_projection)
    b5_trans = Ctrans_MEM(b5, raster_for_projection)
    b6_trans = Ctrans_MEM(b6, raster_for_projection)
    b7_trans = Ctrans_MEM(b7, raster_for_projection)
    cf_trans = Ctrans_MEM(cf, raster_for_projection)
    # #### (3-2) IMAGE CALCULATIONS
    print("Start image calculations, " + item)
    # #### (3-2-1) GET COORDINATE INFO FOR ALL FILES
    cols = b2_trans.RasterXSize
    rows = b2_trans.RasterYSize
    proj = b2_trans.GetProjection()
    geotrans = b2_trans.GetGeoTransform()
    # #### (3-2-2) LOAD ALL FILES INTO ARRAYS
    b2_array = b2_trans.ReadAsArray(0, 0, cols, rows)
    b3_array = b3_trans.ReadAsArray(0, 0, cols, rows)
    b4_array = b4_trans.ReadAsArray(0, 0, cols, rows)
    b5_array = b5_trans.ReadAsArray(0, 0, cols, rows)
    b6_array = b6_trans.ReadAsArray(0, 0, cols, rows)
    b7_array = b7_trans.ReadAsArray(0, 0, cols, rows)
    # #### (3-2-3) ACTIVE AREA MASK --> MEMORY FIRST
    print("Active area, " + item)
    aa = drvMemR.Create('', cols, rows, 1, GDT_Byte)
    aa.SetProjection(proj)
    aa.SetGeoTransform(geotrans)
    # Operation to generate active area
    b2_array_bin = np.empty([rows, cols])
    np.putmask(b2_array_bin, b2_array > 0, 1)
    b3_array_bin = np.empty([rows, cols])
    np.putmask(b3_array_bin, b3_array > 0, 1)
    b4_array_bin = np.empty([rows, cols])
    np.putmask(b4_array_bin, b4_array > 0, 1)
    b5_array_bin = np.empty([rows, cols])
    np.putmask(b5_array_bin, b5_array > 0, 1)
    b6_array_bin = np.empty([rows, cols])
    np.putmask(b6_array_bin, b6_array > 0, 1)
    b7_array_bin = np.empty([rows, cols])
    np.putmask(b7_array_bin, b7_array > 0, 1)
    prod = b2_array_bin * b3_array_bin * b4_array_bin * b5_array_bin * b6_array_bin * b7_array_bin
    # Write active area into MEM file
    aa.GetRasterBand(1).WriteArray(prod, 0, 0)
    # #### (3-2-4) STACK THE MULTISPECTRAL BANDS
    print("Layer stacking, " + item)
    stack_mem = drvMemR.Create('', cols, rows, 6, 3)  # '3' is for 16-bit signed integer
    stack_mem.SetProjection(proj)
    stack_mem.SetGeoTransform(geotrans)
    stack_mem.GetRasterBand(1).WriteArray(b2_array, 0, 0)
    stack_mem.GetRasterBand(2).WriteArray(b3_array, 0, 0)
    stack_mem.GetRasterBand(3).WriteArray(b4_array, 0, 0)
    stack_mem.GetRasterBand(4).WriteArray(b5_array, 0, 0)
    stack_mem.GetRasterBand(5).WriteArray(b6_array, 0, 0)
    stack_mem.GetRasterBand(6).WriteArray(b7_array, 0, 0)
    # #### (3-2-5) CLOUDMASK
    # --> so far it seems that inputval = outputval
    print("Cloud mask, " + item)
    cloud = drvMemR.Create('', cols, rows, 1, GDT_Byte)
    cloud.SetProjection(proj)
    cloud.SetGeoTransform(geotrans)
    cloud.GetRasterBand(1).WriteArray(cf_trans.ReadAsArray(0, 0, cols, rows), 0, 0)
    # #### (3-2-5) CLOUD DISTANCE
    print("Cloud distance, " + item)
    cloudist = drvMemR.Create('', cols, rows, 1, GDT_Int16)
    cloudist.SetProjection(proj)
    cloudist.SetGeoTransform(geotrans)
    cloudband = cloud.GetRasterBand(1)
    cloudist_band = cloudist.GetRasterBand(1)
    # Set options and run the distance
    creationoptions = ['VALUES=2,4', 'DISTUNITS=PIXEL']
    gdal.ComputeProximity(cloudband, cloudist_band, creationoptions)
    # Mask everything outside of active area
    #aa_array = aa.GetRasterBand(1).ReadAsArray(0,0,cols,rows)
    clouddist_array = cloudist_band.ReadAsArray(0, 0, cols, rows)
    clouddist_mask = np.empty([rows, cols])
    np.putmask(clouddist_mask, prod == 1, clouddist_array)
    cloudist.GetRasterBand(1).WriteArray(clouddist_mask, 0, 0)
    # #### (3-2-6) NADIR DISTANCE
    # Get active area file
    print("Nadir distance, " + item)
    nadir_array = np.zeros([rows, cols])
    aa_array = aa.GetRasterBand(1).ReadAsArray(0, 0, cols, rows)
    # Get the upper left point of the area mas
    for row in range(rows):
        for col in range(cols):
            px_val = aa_array[row, col]
            if px_val == 1:
                UL = [row, col]
                break
        else:
            continue
        break
    # Get the lower left
    for col in range(cols):
        for row in reversed(range(rows)):
            px_val = aa_array[row, col]
            if px_val == 1:
                LL = [row, col]
                break
        else:
            continue
        break
    # Get the upper right point
    for col in reversed(range(cols)):
        for row in range(rows):
            px_val = aa_array[row, col]
            if px_val == 1:
                UR = [row, col]
                break
        else:
            continue
        break
    # Get the lower right point
    for row in reversed(range(rows)):
        for col in reversed(range(cols)):
            px_val = aa_array[row, col]
            if px_val == 1:
                LR = [row, col]
                break
        else:
            continue
        break
    # Get the x-coordinates for the nadir
    nadirTopX = (UR[1] + UL[1]) / 2
    nadirBottomX = (LR[1] + LL[1]) / 2
    # Get the nadirTopY
    for row in range(rows):
        px = aa_array[row, nadirTopX]
        if px == 1:
            nadirTopY = row
            break
    # Get the nadirBottomY
    for row in reversed(range(rows)):
        px = aa_array[row, nadirBottomX]
        if px == 1:
            nadirBottomY = row
            break
    # Write points into shapefile in Memory
    # Create shp-file with all properties
    drvMemV = ogr.GetDriverByName('Memory')
    shp_srs = osr.SpatialReference()
    shp_srs.ImportFromWkt(proj)
    shp_mem = drvMemV.CreateDataSource('')
    # Add nadirTop
    NT_x = nadirBottomX * geotrans[1] + geotrans[0] + (geotrans[1] / 2)
    NT_y = nadirBottomY * geotrans[5] + geotrans[3] + (geotrans[5] / 2)
    # Add nadirBottom
    NB_x = nadirTopX * geotrans[1] + geotrans[0] + (geotrans[1] / 2)
    NB_y = nadirTopY * geotrans[5] + geotrans[3] + (geotrans[5] / 2)
    # Write into shapefile
    lyr = shp_mem.CreateLayer('', shp_srs, ogr.wkbLineString)
    lyrDef = lyr.GetLayerDefn()
    fieldDefn = ogr.FieldDefn('ID', ogr.OFTInteger)
    lyr.CreateField(fieldDefn)
    line = ogr.Geometry(ogr.wkbLineString)
    line.AddPoint(NT_x, NT_y)
    line.AddPoint(NB_x, NB_y)
    feat = ogr.Feature(lyrDef)
    feat.SetGeometry(line)
    feat.SetField('ID', 1)
    lyr.CreateFeature(feat)
    # Create raster, rasterize line-shp
    nadir = drvMemR.Create('', cols, rows, 1, GDT_Byte)
    nadir.SetProjection(proj)
    nadir.SetGeoTransform(geotrans)
    rasterize = gdal.RasterizeLayer(nadir, [1], lyr, burn_values=[1])
    # CALCULATE DISTANCE TO NADIR
    # Create raster
    nadir_dis = drvMemR.Create('', cols, rows, 1, GDT_Int16)
    nadir_dis.SetProjection(proj)
    nadir_dis.SetGeoTransform(geotrans)
    nadir_dis_band = nadir_dis.GetRasterBand(1)
    nadir_band = nadir.GetRasterBand(1)
    # Set options and run the distance
    creationoptions = ['VALUES=1', 'DISTUNITS=PIXEL']
    gdal.ComputeProximity(nadir_band, nadir_dis_band, creationoptions)
    # Mask out active area
    nadir_dis_array = nadir_dis_band.ReadAsArray(0, 0, cols, rows)
    nadirdist_mask = np.empty([rows, cols])
    np.putmask(nadirdist_mask, prod == 1, nadir_dis_array)
    nadir_dis.GetRasterBand(1).WriteArray(nadirdist_mask, 0, 0)
    # TIRS --> we take band 10
    print("TIRS, " + item)
    tirs = drvMemR.Create('', cols, rows, 1, 3)
    tirs.SetProjection(proj)
    tirs.SetGeoTransform(geotrans)
    tirs.GetRasterBand(1).WriteArray(b10_trans.ReadAsArray(0, 0, cols, rows), 0, 0)
    # #### (4-3) WRITE TO DISK
    print("Write files to disk, " + item)
    # Define out file format
    outDrv = gdal.GetDriverByName('ENVI')
    # 1) Get File Name root for each scene
    # # Create file list
    fileList = os.listdir(scenePath)
    # # get the name of the xml file as a character
    xmlFile = str([a for a in fileList if a.startswith(item[0:16]) and a.endswith('.xml')])
    # # parse xml file
    tree = ET.parse(scenePath + xmlFile[2:27])
    root = tree.getroot()
    # # get acquisition date
    acq_date = root[0][3].text
    # # Create file Name root
    fileNameRoot = item[3:9] + "_" + acq_date[2:4] + acq_date[5:7] + acq_date[8:10] + "_CAUCASUS_SR"

    # 2) Write the processed files to disk
    # ACTIVE AREA MASK
    aa_out_name = scenePath + "/" + fileNameRoot + "_AA-mask.bsq"
    outDrv.CreateCopy(aa_out_name, aa)
    # STACK
    stack_out_name = scenePath + "/" + fileNameRoot + ".bsq"
    outDrv.CreateCopy(stack_out_name, stack_mem)
    # CLOUDMASK
    cloud_out_name = scenePath + "/" + fileNameRoot + "_CMask.bsq"
    outDrv.CreateCopy(cloud_out_name, cloud)
    # CLOUD DISTANCE
    clouddist_out_name = scenePath + "/" + fileNameRoot + "_CMask_Dist.bsq"
    outDrv.CreateCopy(clouddist_out_name, cloudist)
    # NADIR DISTANCE
    nadirdist_out_name = scenePath + "/" + fileNameRoot + "_Nadir_Dist.bsq"
    outDrv.CreateCopy(nadirdist_out_name, nadir_dis)
    # TIRS
    tirs_out_name = scenePath + "/" + fileNameRoot + "_TIR.bsq"
    outDrv.CreateCopy(tirs_out_name, tirs)

    # (3) COMPRESS ALL FILES EXCEPT THE LANDSAT STACK
    print("Compress ENVI-Files, " + item)
    CompressENVIfile(aa_out_name)
    CompressENVIfile(cloud_out_name)
    CompressENVIfile(clouddist_out_name)
    CompressENVIfile(nadirdist_out_name)
    CompressENVIfile(tirs_out_name)

    # (4) DELETE SHIT
    print("Delete input files, " + item)
    # tiffs
    deleteList = os.listdir(scenePath)
    for file in deleteList:
        if file.endswith(".tif"):
            delete = scenePath + "/" + file
            os.remove(delete)
    # targz archive
    os.remove(target_path)
    print("Done, " + item)

if __name__ == "__main__":
    main()