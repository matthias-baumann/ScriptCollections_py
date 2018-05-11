# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import gdal
from gdalconst import *
from sklearn.preprocessing import Imputer
from sklearn.externals import joblib
import baumiTools as bt
from tqdm import tqdm
import numpy as np
from joblib import Parallel, delayed
# ####################################### FOLDER PATHS AND FUNCTIONS ########################################## #
def GetFilesForTile(tileID, list_of_folders):
        tileList = []
        for folder in list_of_folders:
            for file in bt.baumiFM.GetFilesInFolderWithEnding(folder, (".bsq", ".tif"), False):
                if tileID in file:
                    tilePath = folder + file
                    tileList.append(tilePath)
        return tileList
def WorkerFunction(tileParam):
    # Information for this processing --> which bands of Landsat do we take --> here "clean", meaning that the list of numbers
        #L_bands = [1,2,3,5,6,8,9,11,12]

        L_bands = []
        #L_bands = [3,6,9,12,20,21,24,27,30,36,39,42]
        #L_bands = [1,2,3,4,5,6,7,8,9,10,
        #           11,12,13,14,15,16,17,18,19,20,
        #           21,22,23,24,25,26,27,28,29,30,
        #           31,32,33,34,35,36,37,38,39,40,
        #           41,42,43,44,45,46,47,48,
        #           55,56,57,58,59,60]
    # Print the line as a statment
        print(tileParam[2])
    # Build the layer stack
        files = tileParam[5]
        stack_array = []
    #  --> Take the Landsat first (item # in List), load the bands from "L_bands" into arrays
        L_data = gdal.Open(files[0], GA_ReadOnly)
        cols = L_data.RasterXSize
        rows = L_data.RasterYSize
        for band in L_bands:
            ar = L_data.GetRasterBand(band).ReadAsArray(0, 0, cols, rows)
            stack_array.append(ar)
        # Remote the Landsat-file from the 'files' list
        files.pop(0)
        # Now load the other files into array
        for f in files:
            f_open = gdal.Open(f, GA_ReadOnly)
            cols = f_open.RasterXSize
            rows = f_open.RasterYSize
            ar = f_open.GetRasterBand(1).ReadAsArray(0, 0, cols, rows)
            stack_array.append(ar)
        # Transpose the array so that it is useful for the classification
        predictArray = np.transpose(stack_array, (1,2,0))
        rows, cols, n_bands = predictArray.shape
        n_samples = rows * cols
        predictArray_flat = predictArray.reshape((n_samples, n_bands))
        # Impute missing values
        imputer = Imputer(strategy='mean')
        predictArray_flat = imputer.fit_transform(predictArray_flat)
        # Now get the models from the worker list
        TCmod = tileParam[0]
        SCmod = tileParam[1]
        # Predict the tiles
        TCpredict = TCmod.predict(predictArray_flat)
        SCpredict = SCmod.predict(predictArray_flat)
        TCarray_out = TCpredict.reshape((rows, cols))
        TCarray_out = TCarray_out * 10000
        SCarray_out = SCpredict.reshape((rows, cols))
        SCarray_out = SCarray_out * 10000
        # Create output-files
        drvMemR = gdal.GetDriverByName('MEM')
        TCout = drvMemR.Create('', L_data.RasterXSize, L_data.RasterYSize, 1, GDT_UInt16)
        TCout.SetProjection(L_data.GetProjection())
        TCout.SetGeoTransform(L_data.GetGeoTransform())
        SCout = drvMemR.Create('', L_data.RasterXSize, L_data.RasterYSize, 1, GDT_UInt16)
        SCout.SetProjection(L_data.GetProjection())
        SCout.SetGeoTransform(L_data.GetGeoTransform())
        # Write into files
        TCout.GetRasterBand(1).WriteArray(TCarray_out, 0, 0)
        SCout.GetRasterBand(1).WriteArray(SCarray_out, 0, 0)
        # Flush to disk
        bt.baumiRT.CopyMEMtoDisk(TCout, tileParam[3])
        bt.baumiRT.CopyMEMtoDisk(SCout, tileParam[4])
# ####################################### SET TIME-COUNT ###################################################### #
if __name__ == '__main__':
# ####################################### SET TIME COUNT ###################################################### #
    starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print("--------------------------------------------------------")
    print("Starting process, time:" +  starttime)
    print("")
# ####################################### FOLDER PATHS ######################################################## #
    print("Load GBR-Models...")
    n_cores = 40
    L_tiles_selection = "E:/Baumann/CHACO/_Tiles/ActiveTile_List.txt"
    #GBR_TC = joblib.load("G:/Baumann/_ANALYSES/PercentTreeCover/_01_TreeCover_ShrubCover_Modelling_Version_Landsat_plus_Sentinel_ALL/TC_L_CLEAN_S_CLEAN_CV-results_7500trees.sav")
    #GBR_SC = joblib.load("G:/Baumann/_ANALYSES/PercentTreeCover/_01_TreeCover_ShrubCover_Modelling_Version_Landsat_plus_Sentinel_ALL/SC_L_CLEAN_S_CLEAN_CV-results_7500trees.sav")
    GBR_TC = joblib.load("G:/Baumann/_ANALYSES/PercentTreeCover/_01_TreeCover_ShrubCover_Modelling_Version_Landsat_plus_Sentinel_ALL/TC_L_NONE_S_CLEAN_CV-results_7500trees.sav")
    GBR_SC = joblib.load("G:/Baumann/_ANALYSES/PercentTreeCover/_01_TreeCover_ShrubCover_Modelling_Version_Landsat_plus_Sentinel_ALL/SC_L_NONE_S_CLEAN_CV-results_7500trees.sav")

    layerRootFolder = "E:/Baumann/CHACO/"
    selectedLayers = [layerRootFolder + "_Composite_Landsat8_2015/Metrics_Nov15/",
                      layerRootFolder + "_Composite_Sentinel1_2015/VV_mean/",
                      layerRootFolder + "_Composite_Sentinel1_2015/VH_mean/",
                      layerRootFolder + "_Composite_Sentinel1_2015/VV_median/",
                      layerRootFolder + "_Composite_Sentinel1_2015/VH_median/"]
    #selectedLayers = [layerRootFolder + "_Composite_Landsat8_2015/Metrics_Nov15/"]#,
                      #layerRootFolder + "_Composite_Sentinel1_2015/VV_mean/",
                      #layerRootFolder + "_Composite_Sentinel1_2015/VH_mean/",
                      #layerRootFolder + "_Composite_Sentinel1_2015/VV_stdev/",
                      #layerRootFolder + "_Composite_Sentinel1_2015/VH_stdev/",
                      #layerRootFolder + "_Composite_Sentinel1_2015/VV_median/",
                      #layerRootFolder + "_Composite_Sentinel1_2015/VH_median/",
                      #layerRootFolder + "_Composite_Sentinel1_2015/VV_q25/",
                      #layerRootFolder + "_Composite_Sentinel1_2015/VV_q75/",
                      #layerRootFolder + "_Composite_Sentinel1_2015/VV_q75q25range/",
                      #layerRootFolder + "_Composite_Sentinel1_2015/VH_q25/",
                      #layerRootFolder + "_Composite_Sentinel1_2015/VH_q75/",
                      #layerRootFolder + "_Composite_Sentinel1_2015/VH_q75q25range/"]
    #outputFolder_TC = "G:/Baumann/_ANALYSES/PercentTreeCover/__Run_20170823/L_CLEAN_S_CLEAN__TC/"
    #outputFolder_SC = "G:/Baumann/_ANALYSES/PercentTreeCover/__Run_20170823/L_CLEAN_S_CLEAN__SC/"
    outputFolder_TC = "G:/Baumann/_ANALYSES/PercentTreeCover/__Run_20170823/L_NONE_S_CLEAN__TC/"
    outputFolder_SC = "G:/Baumann/_ANALYSES/PercentTreeCover/__Run_20170823/L_NONE_S_CLEAN__SC/"
# ####################################### PROCESSING ########################################################## #
# (1) BUILD THE JOB-LIST
    print("Build job-list")
    jobList = []
# Get only the active tiles, create for each of the tiles and individual list
    txt_open  = open(L_tiles_selection, "r")
    for line in tqdm(txt_open):
    # Generate a list that has all the information/models for THAT tile
        tile_params = []
        # add models
        tile_params.append(GBR_TC)
        tile_params.append(GBR_SC)
        # Create an output-filenames
        line = line[:-1]
        tile_params.append(line)
        outTC = outputFolder_TC + line + "_TC.tif"
        outSC = outputFolder_SC + line + "_SC.tif"
        tile_params.append(outTC)
        tile_params.append(outSC)
        # Append the inputFiles
        fileList = GetFilesForTile(line, selectedLayers)
        tile_params.append(fileList)
        # Append the tile_params to the jobList
        jobList.append(tile_params)
# (2) EXECUTE THE JOBS
    print("Process tiles")
    #for job in jobList:
    #    WorkerFuntion(job)
    Parallel(n_jobs=n_cores)(delayed(WorkerFunction)(i) for i in jobList)
# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
    print("")
    endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print("--------------------------------------------------------")
    print("--------------------------------------------------------")
    print("start: " + starttime)
    print("end: " + endtime)
    print("")
# ####################################### TEST STUFF ########################################################## #
#     def BuildDS(TCSC, Landsat, Sentinel):
#         # Load the csv into an array, merge to yvar
#         yVar = pd.read_csv(TCSC)
#         if Landsat != None:
#             xLandsat = pd.read_csv(Landsat)
#             yVar = yVar.merge(xLandsat, on='UniqueID', how='left')
#         if Sentinel != None:
#             xSentinel = pd.read_csv(Sentinel)
#             yVar = yVar.merge(xSentinel, on='UniqueID', how='left')
#         # Separate into two arrays --> (1) dependent variable, (2) predictors ; convert into np.arrays, then return
#         target = yVar.iloc[:, 1].values
#         explain = yVar.iloc[:, 2:].values
#         return target, explain
#     sourceFolder = "B:/Projects-and-Publications/Publications/Publications-in-preparation/baumann-etal_Pecent-TreeShrubCover_Chaco/__Analysis_and_Scripts/_Version_Landsat_plus_Sentinel_ALL/"
#     TD_TC = sourceFolder + "TC.csv"
#     TD_SC = sourceFolder + "SC.csv"
#     TD_Landsat_clean = sourceFolder + "DS_L_clean.csv"
#     TD_Sentinel_clean = sourceFolder + "DS_S_clean.csv"
#     TC_y, TC_x = BuildDS(TD_TC, TD_Landsat_clean, TD_Sentinel_clean)
#     print(TC_y[0:5])
#     print("")
#     print(TC_x[0:5])
# ####################################### TEST STUFF ########################################################## #