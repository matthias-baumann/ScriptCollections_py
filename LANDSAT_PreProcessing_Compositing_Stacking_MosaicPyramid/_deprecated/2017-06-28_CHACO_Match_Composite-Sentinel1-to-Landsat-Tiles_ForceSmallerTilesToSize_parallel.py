# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import gdal, ogr, osr
from gdalconst import *
import numpy as np
import baumiTools as bt
from multiprocessing import Pool
# ####################################### DEFINE MAIN FUNCTION ################################################ #
def main():
# ####################################### SET TIME-COUNT ###################################################### #
    starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print("--------------------------------------------------------")
    print("Starting process, time: " + starttime)
    print("")
# ####################################### FILES, FOLDER-PATHS AND PROCESSING DEFINITIONS ###################### #
    L_name = "G:/CHACO/_COMPOSITING/Tiles_as_Polygons.shp"
    S_name = "G:/CHACO/ReprojectedScenes/S1_Preprocessed/VV/_ScenesAsPolygons_V02.shp"
    L_Tiles = bt.baumiVT.CopyToMem(L_name)
    outFolder = "E:/Baumann/CHACO/_Composite_Sentinel1_2015/VV_stdev/"
    S_folder = "G:/CHACO/ReprojectedScenes/S1_Preprocessed/VV/"
    band = 1
    selectMonths = [1,2,3,4,5,6,7,8,9,10,11,12]
    #selectMonths = [5,6,7,8,9,10] # dry season
    #selectMonths = [1,2,3,4,11,12]# wet season
    selectYears = [2015, 2016]
    stat = "stdev"#q75q25range
# ####################################### BUILD LIST TO BE PASSED TO WORKER-FUNCTION ########################## #
    print("Prepare Job-List...")
    workList = []
    L_lyr = L_Tiles.GetLayer()
    L_feat = L_lyr.GetNextFeature()
    while L_feat:
        active = L_feat.GetField("Reprocess")
        if int(active) != 1:
            L_feat = L_lyr.GetNextFeature()
        else:
            tileName = L_feat.GetField("TileIndex")
            tileList = [tileName, L_name, S_name, selectMonths, selectYears, S_folder, outFolder, band, stat]
            workList.append(tileList)
            L_feat = L_lyr.GetNextFeature()
    L_lyr.ResetReading()
    print("Distribute jobs to cores...")
# ####################################### PASS LIST TO WORKER FUNCTION ######################################## #
    pool = Pool(processes=41)
    pool.map(WorkerFunction, workList)
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
# ####################################### DEFINE WORKER FUNCTION ############################################## #
def WorkerFunction(jobList):
# ####################################### EXTRACT ITEMS FROM LIST ############################################# #
    name = jobList[0]
    L_Tiles = bt.baumiVT.CopyToMem(jobList[1])
    S_Tiles = bt.baumiVT.CopyToMem(jobList[2])
    selectMonths = jobList[3]
    selectYears = jobList[4]
    S_folder = jobList[5]
    outFolder = jobList[6]
    band = jobList[7]
    stat = jobList[8]
# ####################################### DEFINE FUNCTIONS AND DRIVERS ######################################## #
    def GetYearMonthDayfromSentinelIndex(string):
        p = string.find("_2")
        string = string[p + 1:]
        # print(string)
        year = int(string[0:4])
        month = int(string[4:6])
        day = int(string[6:8])
        return year, month, day
    def GetS1arrayForTile(feature, rasterPath, band):
        # get needed proporties of files
        pxSize = 30
        geom = feature.GetGeometryRef()
        rasOpen = gdal.Open(rasterPath, GA_ReadOnly)
        spatialRef = geom.GetSpatialReference()
        dtype = rasOpen.GetRasterBand(band).DataType
        # Build SHP-file in memory from the geometry
        shpMem = drvMemV.CreateDataSource('')
        shpMem_lyr = shpMem.CreateLayer('shpMem', spatialRef, geom_type=ogr.wkbMultiPolygon)
        shpMem_lyr_defn = shpMem_lyr.GetLayerDefn()
        shpMem_feat = ogr.Feature(shpMem_lyr_defn)
        shpMem_feat.SetGeometry(geom)
        shpMem_lyr.CreateFeature(shpMem_feat)
        # Build 30m Landsat raster from the new SHP-file
        x_min, x_max, y_min, y_max = shpMem_lyr.GetExtent()
        x_res = int((x_max - x_min) / pxSize) + 1
        y_res = int((y_max - y_min) / pxSize)
        shpMem_asRaster = drvMemR.Create('', x_res, y_res, gdal.GDT_Byte)
        shpMem_asRaster.SetProjection(str(spatialRef))
        shpMem_asRaster.SetGeoTransform((x_min, pxSize, 0, y_max, 0, -pxSize))
        shpMem_asRaster_b = shpMem_asRaster.GetRasterBand(1)
        shpMem_asRaster_b.SetNoDataValue(0)
        gdal.RasterizeLayer(shpMem_asRaster, [1], shpMem_lyr, burn_values=[1])
        shpMem_array = np.array(shpMem_asRaster_b.ReadAsArray())
        # Subset the inputRaster raster and load it into the array
        rasMem = drvMemR.Create('', shpMem_asRaster.RasterXSize, shpMem_asRaster.RasterYSize, 1, dtype)
        rasMem.SetGeoTransform(shpMem_asRaster.GetGeoTransform())
        rasMem.SetProjection(shpMem_asRaster.GetProjection())
        gdal.ReprojectImage(rasOpen, rasMem, rasOpen.GetProjection(), shpMem_asRaster.GetProjection(), gdal.GRA_Average)
        # bt.baumiRT.CopyMEMtoDisk(rasMem, "E:/Baumann/CHACO/_Composite_Sentinel1_2015_new/HH/3.tif")
        rasMem_array = np.array(rasMem.GetRasterBand(band).ReadAsArray())
        outList = [rasMem, rasMem_array]
        return outList
    def CalculateMetric(listOfArrays, function, minLimit, maxLimit):
        # Mask out 0 and 1 and flag them as DatIgnoreValues
        if len(listOfArrays) >= 1:
            if function == "mean":
                stack = np.dstack(listOfArrays)
                mask = np.ma.masked_less_equal(stack, minLimit)
                mask = np.ma.masked_greater_equal(mask, maxLimit)
                value = np.ma.mean(mask, axis=2)
            if function == "median":
                stack = np.dstack(listOfArrays)
                mask = np.ma.masked_less_equal(stack, minLimit)
                mask = np.ma.masked_greater_equal(mask, maxLimit)
                value = np.ma.median(mask, axis=2)
            if function == "max":
                stack = np.dstack(listOfArrays)
                mask = np.ma.masked_less_equal(stack, minLimit)
                mask = np.ma.masked_greater_equal(mask, maxLimit)
                value = np.ma.max(mask, axis=2)
            if function == "stdev":
                stack = np.dstack(listOfArrays)
                mask = np.ma.masked_less_equal(stack, minLimit)
                mask = np.ma.masked_greater_equal(mask, maxLimit)
                value = np.ma.std(mask, axis=2)
            if function == "q25":
                stack = np.dstack(listOfArrays)
                mask = np.ma.masked_less_equal(stack, minLimit)
                mask = np.ma.filled(mask, np.nan)
                mask = np.ma.masked_greater_equal(mask, maxLimit)
                mask = np.ma.filled(mask, np.nan)
                value = np.nanpercentile(mask, 25, axis=2)
            if function == "q75":
                stack = np.dstack(listOfArrays)
                mask = np.ma.masked_less_equal(stack, minLimit)
                mask = np.ma.filled(mask,np.nan)
                mask = np.ma.masked_greater_equal(mask, maxLimit)
                mask = np.ma.filled(mask, np.nan)
                value = np.nanpercentile(mask, 75, axis=2)
            if function == 'q75q25range':
                stack = np.dstack(listOfArrays)
                mask = np.ma.masked_less_equal(stack, minLimit)
                mask = np.ma.filled(mask,np.nan)
                mask = np.ma.masked_greater_equal(mask, maxLimit)
                mask = np.ma.filled(mask, np.nan)
                p25 = np.nanpercentile(mask, 25, axis=2)
                p75 = np.nanpercentile(mask, 75, axis=2)
                value = p75 - p25

        else:
            value = None
        return value
    def ConvertMetricToRaster(array, raster):
        # rasOpen = gdal.Open(raster)
        raster.GetRasterBand(1).WriteArray(array, 0, 0)
        return raster
    drvV = ogr.GetDriverByName('ESRI Shapefile')
    drvMemV = ogr.GetDriverByName('Memory')
    drvMemR = gdal.GetDriverByName('MEM')
# ####################################### PROCESS ITEM ######################## #
    L_lyr = L_Tiles.GetLayer()
    S_lyr = S_Tiles.GetLayer()
    L_PR = L_lyr.GetSpatialRef()
    S_PR = S_lyr.GetSpatialRef()
    transform = osr.CoordinateTransformation(L_PR, S_PR)
    feat_L = L_lyr.GetNextFeature()
    while feat_L:
    # Check if it is the one that we want to process, otherwise skip
        index = feat_L.GetField("TileIndex")
        if index != name:
            feat_L = L_lyr.GetNextFeature()
        else:
            print(index)
            geom = feat_L.GetGeometryRef()
            geom_clone = geom.Clone()
    # Check which scenes we have intersecting in that tile
            geom_clone.Transform(transform)
            S_lyr.SetSpatialFilter(geom_clone)
    # Make a list of the Sentinel-Tiffs that intersect with the Landsat tile
            S1_names = []
            feat_S = S_lyr.GetNextFeature()
            while feat_S:
                name = feat_S.GetField("TileIndex")
                S1tilePath = S_folder + name
                S1_names.append(S1tilePath)
                feat_S = S_lyr.GetNextFeature()
            S_lyr.ResetReading()
            S1_select = []
            for n in S1_names:
                year, month, day = GetYearMonthDayfromSentinelIndex(n)
                if year in selectYears and month in selectMonths:
                    S1_select.append(n)
    # Now load the files as arrays into list, crop them prior to that
            arrayList = []
            for S1 in S1_select:
                array = GetS1arrayForTile(feat_L, S1, band)
                arrayList.append(array[1])
            statistic = CalculateMetric(arrayList, stat, 0.005, 4)# vorher: 0.0001, 0.001
    # Write output array --> use output from GetS1arryForTile()[0]
            if statistic == None:
                feat_L = L_lyr.GetNextFeature()
            else:
                outras = ConvertMetricToRaster(statistic, array[0])
                bt.baumiRT.CopyMEMtoDisk(outras, outFolder + index + ".tif")
                S_lyr.ResetReading()
                feat_L = L_lyr.GetNextFeature()
# ####################################### EXECUTE MAIN FUNCTION ############################################### #
if __name__ == "__main__":
    main()