# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time, os
import gdal, ogr
import baumiTools as bt
from tqdm import tqdm
import numpy as np
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.externals import joblib
from joblib import Parallel, delayed
from gdalconst import *
# ####################################### FUNCTIONS ########################################################### #
def Workerfunction(tile_parameters):
    # Extract the information we need to classify
    model = tile_parameters[0]
    tileID = tile_parameters[1]
    print(tileID)
    outpath = tile_parameters[2]
    ds_paths = tile_parameters[3]
    # Change the model parameterizations
    model.set_params(n_jobs=15, verbose=False)
    # Take the first dataset to get the necessary information --> cols, rows, pr, gt, also number of bands by looping through the list of pasths
    ds_open = gdal.Open(ds_paths[0][0])
    cols = ds_open.RasterXSize
    rows = ds_open.RasterYSize
    pr = ds_open.GetProjection()
    gt = ds_open.GetGeoTransform()
    ds_open = None
    bandsALL = 0
    for ds in ds_paths:
        nbands = len(ds[1])
        bandsALL = bandsALL + nbands
    # Initialize an empty array which we populate with data
    stack_array = np.ones((rows * cols, bandsALL), dtype=np.int16)
    i = 0
    for ds in ds_paths:
        path = ds[0]
        bands = ds[1]
        ds_open = gdal.Open(path, GA_ReadOnly)
        for band in bands:
            ar = ds_open.GetRasterBand(band).ReadAsArray(0, 0, cols, rows).ravel()
        # Check if it is a sentinel-1 band --> then multiply values by 10000
            if path.find("Sentinel1") >= 0:
                ar = ar * 10000
            else:
                ar = ar
            stack_array[:, i] = ar
            i=i+1
        ds_open = None
    prediction = model.predict(stack_array)
    stack_array = None
    prediction = prediction.reshape((rows, cols))
    # Create output-files
    drvMemR = gdal.GetDriverByName('MEM')
    out = drvMemR.Create('', cols, rows, 1, GDT_Byte)
    out.SetProjection(pr)
    out.SetGeoTransform(gt)
    # Write into files
    out.GetRasterBand(1).WriteArray(prediction, 0, 0)
    # Flush to disk
    bt.baumiRT.CopyMEMtoDisk(out, outpath)
# ####################################### SET TIME-COUNT ###################################################### #
if __name__ == '__main__':
    starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print("--------------------------------------------------------")
    print("Starting process, time: " +  starttime)
    print("")
# ####################################### DRIVERS AND FOLDER-PATHS ############################################ #
    rootFolder = "G:/Baumann/_ANALYSES/LandUseChange_1985-2000-2015_UpdateWithRadar/Classification"
    nr_cores = 50
    drvR = gdal.GetDriverByName('GTiff')
    drvMemR = gdal.GetDriverByName('MEM')
    drvMemV = ogr.GetDriverByName('Memory')
    outTiles = rootFolder + "/Run_03/Tiles/"
    rs_rootFolder = "E:/Baumann/CHACO/"
    ativeTiles = rs_rootFolder + "_Tiles/ActiveTile_List.txt"
# ####################################### CLASSIFICATION DEFINITIONS ########################################## #
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
                       ["_Composite_Sentinel1_2015/VH_stdev/", "SAR_2015_VHstdev", [1]],
                       ["_Composite_Sentinel1_2015/VV_stdev/", "SAR_2015_VVstdev", [1]]                       ]
    outClassModel = rootFolder + "/Run_03/RF_model_20180223_bestMod.sav"
    outClassGridSearch = rootFolder + "/Run_03/RF_model_20180223.sav"
# ####################################### PROCESSING ########################################################## #
    # Check if the classification model already exists, then skip the process below
    if not os.path.exists(outClassModel):
#### (1) LOAD THE TRAINING DATA FROM THE NUMPY ARRAYS INTO INDIVIDUAL LISTS
        print("Load training data...")
        labelList = bt.baumiFM.GetFilesInFolderWithEnding(rootFolder + "/Run_03/10000_PpC/", "Labels.npy", True)
        valueList = bt.baumiFM.GetFilesInFolderWithEnding(rootFolder + "/Run_03/10000_PpC/", "Values.npy", True)
    # Make sure we get the correct order --> solve it by creating a list of the class-numbers that we sequentially work on --> skip "_01_" because we load it manually
        classList = ["_02_", "_03_", "_04_", "_05_", "_06_", "_07_", "_08_", "_09_", "_10_", "_11_", "_12_",
                 "_13_", "_14_", "_15_", "_16_", "_17_", "_18_", "_19_", "_20_", "_21_", "_22_", "_23_"]
        print("Labels")
        time.sleep(1)
        label_arr = np.load([file for file in labelList if file.find("_01_") >= 0][0])
        for c in tqdm(classList):
            arr = np.load([file for file in labelList if file.find(c) >= 0][0])
            indices = np.random.randint(0, arr.shape[0], 5000)
            arr = arr[indices]
            label_arr = np.append(label_arr, arr, axis=0)
        time.sleep(1)
        print("Values")
        value_arr = np.load([file for file in valueList if file.find("_01_") >= 0][0]).astype(np.int64)
        for c in tqdm(classList):
            arr = np.load([file for file in valueList if file.find(c) >= 0][0]).astype(np.int64)
            # Get only a subset of 5000points for the classification
            indices = np.random.randint(0, arr.shape[0], 5000)
            arr = arr[indices]
            value_arr = np.append(value_arr, arr, axis=0)
        time.sleep(1)
        print("DONE!")
        print("")
#### (2) PARAMETERIZE CLASSIFIER
        print("Parameterizing classifier")
        param_grid_RF = {'n_estimators': [100, 250, 500, 750, 1000],
                         'min_samples_split': [2, 5, 10],
                         'max_features': [15, 20]}# sqrt(n_features) --> guidance from scikit-learn
    # Apply GridSearchCV using the parameter-grid from above and fit the model
        RF = RandomForestClassifier(verbose=True)
        RF_cv = GridSearchCV(RF, param_grid = param_grid_RF, cv = 10, refit=True, n_jobs = nr_cores) \
        .fit(value_arr, label_arr)
    # Get best model
        RF_bestMod = RF_cv.best_estimator_
    # Write outputs to disk
        joblib.dump(RF_bestMod, outClassModel)
        joblib.dump(RF_cv, outClassGridSearch)
        print("DONE!")
        print("")
    else:
        print("--> Found model. Skipping parameterization, loading existing model instead...")
        time.sleep(1)
        RF_bestMod = joblib.load(outClassModel)
        print("")
#### (3) BUILD JOBLIST TO BE PASSED TO THE CLUSTER
    print("Build classification joblist to pass to cluster")
    jobList = []
# Get only the active tiles, create for each of the tiles and individual list
    txt_open  = open(ativeTiles, "r")
    for line in tqdm(txt_open):
# Generate a list that has all the information/models for THAT tile
        tile_job = []
    # add model
        tile_job.append(RF_bestMod)#outClassModel
    # Create an output-filenames
        #line = line[:-1]
        line = line[:-17]
        tile_job.append(line)   # Tile-ID
        outTile = outTiles + line + ".tif"  # Output-path for tile
        tile_job.append(outTile)
    # Append the inputFile
        fileList = []   # Files
        for folder in tileFolders:
            folderPath = rs_rootFolder + folder[0]
            bands = folder[2]
            for file in bt.baumiFM.GetFilesInFolderWithEnding(folderPath, (".bsq", ".tif"), False):
                if line in file:
                    tilePath = folderPath + file
                    pathBand = [tilePath, bands]
                    fileList.append(pathBand)
        tile_job.append(fileList)
    # Append the tile_job to the jobList
        jobList.append(tile_job)
    time.sleep(1)
    print("DONE!")
    print("")
#### (4) PASS JOBLIST TO THE CLUSTER
# Change the number of parallel tiles --> we want less tile processed at the same time with more parallel processors running
# This also means that we have to modify the classifier in the Workerfunction --> change to 10
    print("Classifying...")
    nr_cores = 4
    Parallel(n_jobs=nr_cores)(delayed(Workerfunction)(i) for i in jobList)
    #for job in jobList:
    #    Workerfunction(job)
# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
    print("")
    endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print("--------------------------------------------------------")
    print("--------------------------------------------------------")
    print("start: " + starttime)
    print("end: " + endtime)
    print("")