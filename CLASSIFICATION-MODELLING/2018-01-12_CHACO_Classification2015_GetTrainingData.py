# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time, os
import osr, ogr
import struct
import baumiTools as bt
from joblib import Parallel, delayed
import numpy as np
from tqdm import tqdm
# start: Starting process, time:Mon, 15 Jan 2018 09:49:03
# ####################################### FUNCTIONS ########################################################### #
def WorkerFunction(params):
# Extract the parameters, load files and layers
    shapeName = params[0]
    SHP_p = bt.baumiVT.CopyToMem(shapeName)
    LYR_p = SHP_p.GetLayer()
    SR_p = LYR_p.GetSpatialRef()
    SHP_t = bt.baumiVT.CopyToMem(params[3])
    LYR_t = SHP_t.GetLayer()
    rootFolder = params[1]
    compos = params[2]
    outFolder = params[4]
# Set a timer for the process
    timer1 = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print(params[0], "   Start:", timer1)
# Build the output-lists in memory
    labels = []
    values = []
    IDs = []
# Get the information for storage, etc.
    p1 = shapeName.rfind("/")
    classVal = int(shapeName[p1 + 1:p1 + 3])
    classVal_str = shapeName[p1 + 1:p1 + 3]
    p2 = shapeName.rfind(".")
    classLab = shapeName[p1 + 4:p2]
## Loop through the different polygons, check if they contain a point. If YES, then do the operation, if NO then go to next feature
    FEAT_t = LYR_t.GetNextFeature()
    while FEAT_t:
    # Set spatial filter
        GEOM_t = FEAT_t.GetGeometryRef()
        LYR_p.SetSpatialFilter(GEOM_t)
    # Check if the feature count is greater than 0, if YES, then go to next feature
        if LYR_p.GetFeatureCount() == 0:
            FEAT_t = LYR_t.GetNextFeature()
            LYR_p.ResetReading()
        else:
        # Since  there are points intersecting with the polygon, we load the rasters into a list of rasters in memory
            rasList = []
            # Get the tile name
            tileID = FEAT_t.GetField("TileIndex")
            tileID = tileID[:-15]
            for ras in compos:
                # Load the correct tile from the raster
                path = ras[0]
                tile = [rootFolder + path + t for t in os.listdir(rootFolder + path) if t.find(tileID) >= 0 and not t.endswith(".hdr")]
                rasProp = [bt.baumiRT.OpenRasterToMemory(tile[0]), ras[2], tile[0]] # ras[2] refers to the bands for this particular raster
                rasList.append(rasProp)
            # Now loop over each of the point features that intersect and get the raster values
            FEAT_p = LYR_p.GetNextFeature()
            while FEAT_p:
                # Load the geometry, get the ID-value from it, so that we can add it to the list
                GEOM_p = FEAT_p.GetGeometryRef()
                geomID = FEAT_p.GetField("ID")
                #print(geomID)
                rasVals = []
                for ras in rasList:
                    ds = ras[0]
                    pr = ds.GetProjection()
                    gt = ds.GetGeoTransform()
                # Check if the raster is a Sentinel-1 image, so that we later multiply the extracted values by 10,000
                    if ras[2].find("Sentinel1") >= 0:
                        S1_adj = 1
                    else:
                        S1_adj = 0
                # Build a coordinate transformation, get coordinate of point
                    target_SR = osr.SpatialReference()
                    target_SR.ImportFromWkt(pr)
                    coordTrans = osr.CoordinateTransformation(SR_p, target_SR)
                    GEOM_p_clone = GEOM_p.Clone()
                    GEOM_p_clone.Transform(coordTrans)
                    mx, my = GEOM_p_clone.GetX(), GEOM_p_clone.GetY()
                    px = int((mx - gt[0]) / gt[1])
                    py = int((my - gt[3]) / gt[5])
                # Extract the points band by band
                    for b in ras[1]:
                        # Get the value
                        rb = ds.GetRasterBand(b)
                        rb_dType = bt.baumiRT.GetDataTypeHexaDec(rb.DataType)
                        try:
                            structVar = rb.ReadRaster(px, py, 1, 1)
                            val = struct.unpack(rb_dType, structVar)[0]
                            if S1_adj == 1:
                                val = int(val * 10000)
                            else:
                                val = val
                            rasVals.append(val)
                        except:
                            #could be that the point is on a tile boundary. Move it manually py one pixel
                            rasVals.append(9999)
    # Append the three types of information to the respective list, then take next feature
                labels.append(classVal)
                values.append(rasVals)
                IDs.append(geomID)
                FEAT_p = LYR_p.GetNextFeature()
            # Reset reading for LYR_p, so that it starts next time at zero again
            LYR_p.ResetReading()
            # take next feature in polygon-layer
            FEAT_t = LYR_t.GetNextFeature()
    # Reset the reading of the SHP-file, then convert lists to arrays
    labels_arr = np.asarray(labels)
    values_arr = np.asarray(values)
    ids_arr = np.asarray(IDs)
    # Flush to disk
    outLabels = outFolder + "_" + classVal_str + "_" + classLab + "_Labels.npy"
    np.save(outLabels, labels_arr)
    outValues = outFolder + "_" + classVal_str + "_" + classLab + "_Values.npy"
    np.save(outValues, values_arr)
    outIDs = outFolder + "_" + classVal_str + "_" + classLab + "_IDs.npy"
    np.save(outIDs, ids_arr)
# Set timer to give the estimate on how long it took
    timer2 = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print(params[0], "  Start:", timer1, "    End:", timer2)
# ####################################### SET TIME-COUNT ###################################################### #
if __name__ == '__main__':
    starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print("--------------------------------------------------------")
    print("Starting process, time:" +  starttime)
    print("")
# ####################################### FOLDERS AND FILES ################################################### #
    n_cores = 23
    TD_folder = "G:/Baumann/_ANALYSES/LandUseChange_1985-2000-2015_UpdateWithRadar/Classification/Run_03/10000_PpC/"
    compRoots = "E:/Baumann/CHACO/"
    AT_shp = "E:/Baumann/CHACO/_Tiles/Tiles_as_Polygons.shp"
    tileFolders = [#["_Composites_Landsat457_85-90-95-00-05-10-13/1985_Dry-Season_DOY190/BPC/", "L_1985_Dry", [1,2,3,4,5,6]],
                   #["_Composites_Landsat457_85-90-95-00-05-10-13/1985_Wet-Season_DOY015/BPC/", "L_1985_Wet", [1,2,3,4,5,6]],
                   ["_Composites_Landsat457_85-90-95-00-05-10-13/1985_Metrics/", "L_1985_metrics",
                    [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,
                     31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,55,56,57,58,59,60]],
                   #["_Composites_Landsat457_85-90-95-00-05-10-13/2000_Dry-Season_DOY190/BPC/", "L_2000_Dry", [1,2,3,4,5,6]],
                   #["_Composites_Landsat457_85-90-95-00-05-10-13/2000_Wet-Season_DOY015/BPC/", "L_2000_Wet", [1,2,3,4,5,6]],
                   ["_Composites_Landsat457_85-90-95-00-05-10-13/2000_Metrics/", "L_2000_metrics",
                    [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,
                     31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,55,56,57,58,59,60]],
                   #["_Composite_Landsat8_2015/DOY196_Jul15/", "L_2015_Dry", [1,2,3,4,5,6]],
                   #["_Composite_Landsat8_2015/DOY015_Jan15/", "L_2015_Wet", [1,2,3,4,5,6]],
                   ["_Composite_Landsat8_2015/Metrics_Nov15/", "L_2015_metrics",
                    [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,
                     31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,55,56,57,58,59,60]],
                   ["_Composite_Sentinel1_2015/VH_mean/", "SAR_2015_VHmean", [1]],
                   ["_Composite_Sentinel1_2015/VV_mean/", "SAR_2015_VVmean", [1]],
                   ["_Composite_Sentinel1_2015/VH_median/", "SAR_2015_VHmedian", [1]],
                   ["_Composite_Sentinel1_2015/VV_median/", "SAR_2015_VVmedian", [1]],
                   #["_Composite_Sentinel1_2015/VH_q25/", "SAR_2015_VHq25", [1]],
                   #["_Composite_Sentinel1_2015/VV_q25/", "SAR_2015_VVq25", [1]],
                   #["_Composite_Sentinel1_2015/VH_q75/", "SAR_2015_VHq75", [1]],
                   #["_Composite_Sentinel1_2015/VV_q75/", "SAR_2015_VVq75", [1]],
                   #["_Composite_Sentinel1_2015/VH_q75q25range/", "SAR_2015_VHq75q25range", [1]],
                   #["_Composite_Sentinel1_2015/VV_q75q25range/", "SAR_2015_VVq75q25range", [1]],
                   ["_Composite_Sentinel1_2015/VH_stdev/", "SAR_2015_VHstdev", [1]],
                   ["_Composite_Sentinel1_2015/VV_stdev/", "SAR_2015_VVstdev", [1]]
                   ]
# ####################################### PROCESSING ########################################################## #
    print("Check shapefiles for double-tile assignment")
    SHPlist = bt.baumiFM.GetFilesInFolderWithEnding(TD_folder, ".shp", True)
    tilesTMP = bt.baumiVT.CopyToMem(AT_shp)
    for SHP in SHPlist:
        print(SHP)
        drvMemV = ogr.GetDriverByName('Memory')
        SHP = ogr.Open(SHP,1)
        LYR_p = SHP.GetLayer()
        LYR_t = tilesTMP.GetLayer()
    # Check for each point whether it intersects with two tiles, if it does, move it by 1m
        feat_p = LYR_p.GetNextFeature()
        while feat_p:
            geom = feat_p.GetGeometryRef()
            LYR_t.SetSpatialFilter(geom)
            # Check if the feature count is greater than 1, if YES, then go to next feature
            if LYR_t.GetFeatureCount() == 1:
               # it it intersects only with one tile, then
                feat_p = LYR_p.GetNextFeature()
                LYR_t.ResetReading()
            else:
            # if >1 then move the feature by one meter left and up
                print("change")
                x, y = geom.GetX(), geom.GetY()
                x = x + 10
                y = y - 10
                geom = ogr.Geometry(ogr.wkbPoint)
                geom.AddPoint(x, y)
                feat_p.SetGeometry(geom)
                LYR_p.SetFeature(feat_p)
                # take next feaeture
                feat_p = LYR_p.GetNextFeature()
    print("Build  job-List")
    joblist = []
    for SHP in SHPlist:
        job = [SHP, compRoots, tileFolders, AT_shp, TD_folder]
        joblist.append(job)
    print("Distribute Jobs. Overall ", str(len(SHPlist)), " jobs to distribute.")
    #### Process the jobs parallel ####
    processed = Parallel(n_jobs=n_cores)(delayed(WorkerFunction)(i) for i in joblist)
# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
    print("")
    endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print("--------------------------------------------------------")
    print("--------------------------------------------------------")
    print("start: " + starttime)
    print("end: " + endtime)
    print("")