# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time, os
import gdal, ogr
from gdalconst import *
import numpy as np
import baumiTools as bt
import math
import pandas as pd
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.externals import joblib
from sklearn import metrics
import matplotlib.pyplot as plt
#from matplotlib.pylab import rcParams
#rcParams['figure.figsize'] = 12, 4
#import seaborn as sns; sns.set()
# ####################################### FUNCTIONS ########################################################### #
def Parameterize(TD, TDstring, LandsatData, SentinelData, source_folder, prefix, statTable, counter, n_cores):
    # Functions we need in the Parameterize function
    def BuildDS(TCSC, Landsat, Sentinel):
        # Load the csv into an array, merge to yvar
        yVar = pd.read_csv(TCSC)
        if Landsat != None:
            xLandsat = pd.read_csv(Landsat)
            yVar = yVar.merge(xLandsat, on='UniqueID', how='left')
        if Sentinel != None:
            xSentinel = pd.read_csv(Sentinel)
            yVar = yVar.merge(xSentinel, on='UniqueID', how='left')
        # Separate into two arrays --> (1) dependent variable, (2) predictors ; convert into np.arrays, then return
        target = yVar.iloc[:, 1].values
        explain = yVar.iloc[:, 2:].values

        print(target[0:5])
        print(explain[0:5])
        exit(0)

        return target, explain
    def Model(yValues, predictors, CVout, nCores):
        if os.path.exists(CVout):
            print("--> Found model from previous run, using that one.")
            gs_cv = joblib.load(CVout)
        else:
            param_grid = {'learning_rate': [0.1, 0.05, 0.02, 0.01, 0.005, 0.002, 0.001],
                          'max_depth': [4, 6],
                          'min_samples_leaf': [3, 5, 9, 17],
                          'max_features': [1.0, 0.5, 0.3, 0.1]}
            est = GradientBoostingRegressor(n_estimators=7500)
            gs_cv = GridSearchCV(est, param_grid, cv=10, refit=True, n_jobs=nCores) \
                .fit(predictors, yValues)
            # Write outputs to disk and return elements from function
            joblib.dump(gs_cv, CVout)

        return (gs_cv)
    def ModelPerformance(cv_results, yData, xData):
        # Produce pandas-table entailing all model-parameterizations
        cv_scoreTable = cv_results.cv_results_
        cv_scoreTable_pd = pd.DataFrame(cv_scoreTable)
        # Get parameters from the best estimator
        md = cv_results.best_params_['max_depth']
        lr = cv_results.best_params_['learning_rate']
        msl = cv_results.best_params_['min_samples_leaf']
        mf = cv_results.best_params_['max_features']
        # Calculate Predictions of the true values
        y_true, y_pred = yData, cv_results.predict(xData)
        # plt.scatter(y_true, y_pred, color='black')
        # plt.show()
        # Extract R2 and MSE
        R2 = metrics.r2_score(y_true, y_pred)
        mse = metrics.mean_squared_error(y_true, y_pred)
        # print(R2, mse)
        # merge y_true, y_pred into pandas table
        corr_table = pd.DataFrame({'y_True': y_true, 'y_pred': y_pred})
        # print(corr_table[1:5])
        return [R2, mse, md, lr, msl, mf, corr_table]
    # Do the parameterization
    TC_y, TC_x = BuildDS(TD, LandsatData, SentinelData)
    print("Exhaustive GridSearch to fit model --> ", prefix)
    modGridSearchCV = Model(TC_y, TC_x, source_folder + prefix + "_CV-results_7500trees.sav", n_cores)
    print("Get Model Performance")
    modelOut = ModelPerformance(modGridSearchCV, TC_y, TC_x)
    statTable.loc[counter] = (
    prefix, TDstring, modelOut[0], modelOut[1], modelOut[2], modelOut[3], modelOut[4], modelOut[5])
    corrTab = modelOut[6]
    corrTab.to_csv(source_folder + prefix + "_CV-results_7500trees.csv", sep=",")
    return statTable

# ####################################### SET TIME-COUNT ###################################################### #
if __name__ == '__main__':
    starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print("--------------------------------------------------------")
    print("Starting process, time: " +  starttime)
    print("")
# ####################################### DRIVERS AND FOLDER-PATHS ############################################ #
    sourceFolder = "G:/Baumann/_ANALYSES/PercentTreeCover/_01_TreeCover_ShrubCover_Modelling_Version_Landsat_plus_Sentinel_ALL/"
    nr_cores = 40
    drvR = gdal.GetDriverByName('GTiff')
    drvMemR = gdal.GetDriverByName('MEM')
    drvMemV = ogr.GetDriverByName('Memory')
    TD_Landsat_clean = sourceFolder + "DS_L_clean_v02.csv"
    TD_Landsat_all = sourceFolder + "DS_L_full.csv"
    TD_Sentinel_clean = sourceFolder + "DS_S_clean.csv"
    TD_Sentinel_all = sourceFolder + "DS_S_full.csv"
    TD_TC = sourceFolder + "TC.csv"
    TD_SC = sourceFolder + "SC.csv"
# ####################################### PROCESSING ########################################################## #
## TRAIN THE REGRESSOR FOR THE DIFFERENT COMBINATIONS
# (1) Create an output array (as Pandas-Table) where to put the data in
    outDF = pd.DataFrame(columns=('Combination', 'Variable', 'CV_R2', 'CV_MSE', 'MaxDepth', 'learningRate', 'MinSamplesLeaf', 'MaxFeatures'))
    i=1
# (2) Process the different combinations
# (2-1) Landsat_ALL_SENTINEL_ALL
    #prefix = "TC_L_ALL_S_ALL"
    #outDF = Parameterize(TD_TC, "TC", TD_Landsat_all, TD_Sentinel_all, sourceFolder, prefix, outDF, i, nr_cores)
    #i = i+1
    #prefix = "SC_L_ALL_S_ALL"
    #outDF = Parameterize(TD_SC, "SC", TD_Landsat_all, TD_Sentinel_all, sourceFolder, prefix, outDF, i, nr_cores)
    #i = i+1
# (2-2) Landsat_CLEAN_SENTINEL_CLEAN
    #prefix = "TC_L_CLEAN_S_CLEAN"
    #outDF = Parameterize(TD_TC, "TC", TD_Landsat_clean, TD_Sentinel_clean, sourceFolder, prefix, outDF, i, nr_cores)
    #i = i + 1
    #prefix = "SC_L_CLEAN_S_CLEAN"
    #outDF = Parameterize(TD_SC, "SC", TD_Landsat_clean, TD_Sentinel_clean, sourceFolder, prefix, outDF, i, nr_cores)
    #i = i + 1
# (2-3) Landsat_ALL_SENTINEL_CLEAN
    #prefix = "TC_L_ALL_S_CLEAN"
    #outDF = Parameterize(TD_TC, "TC", TD_Landsat_all, TD_Sentinel_clean, sourceFolder, prefix, outDF, i, nr_cores)
    #i = i + 1
    #prefix = "SC_L_ALL_S_CLEAN"
    #outDF = Parameterize(TD_SC, "SC", TD_Landsat_all, TD_Sentinel_clean, sourceFolder, prefix, outDF, i, nr_cores)
    #i = i + 1
# (2-4) Landsat_ALL_SENTINEL_NONE
    #prefix = "TC_L_ALL_S_NONE"
    #outDF = Parameterize(TD_TC, "TC", TD_Landsat_all, None, sourceFolder, prefix, outDF, i, nr_cores)
    #i = i + 1
    #prefix = "SC_L_ALL_S_NONE"
    #outDF = Parameterize(TD_SC, "SC", TD_Landsat_all, None, sourceFolder, prefix, outDF, i, nr_cores)
    #i = i + 1
# (2-5) Landsat_CLEAN_SENTINEL_ALL
    #prefix = "TC_L_CLEAN_S_ALL"
    #outDF = Parameterize(TD_TC, "TC", TD_Landsat_clean, TD_Sentinel_all, sourceFolder, prefix, outDF, i, nr_cores)
    #i = i + 1
    #prefix = "SC_L_CLEAN_S_ALL"
    #outDF = Parameterize(TD_SC, "SC", TD_Landsat_clean, TD_Sentinel_all, sourceFolder, prefix, outDF, i, nr_cores)
    #i = i + 1
# (2-6) Landsat_CLEAN_SENTINEL_NONE
    prefix = "TC_L_CLEAN_S_NONE_v02"
    outDF = Parameterize(TD_TC, "TC", TD_Landsat_clean, None, sourceFolder, prefix, outDF, i, nr_cores)
    i = i + 1
    prefix = "SC_L_CLEAN_S_NONE_v02"
    outDF = Parameterize(TD_SC, "SC", TD_Landsat_clean, None, sourceFolder, prefix, outDF, i, nr_cores)
    i = i + 1
# (2-7) Landsat_NONE_SENTINEL_ALL
    #prefix = "TC_L_NONE_S_ALL"
    #outDF = Parameterize(TD_TC, "TC", None, TD_Sentinel_all, sourceFolder, prefix, outDF, i, nr_cores)
    #i = i + 1
    #prefix = "SC_L_NONE_S_ALL"
    #outDF = Parameterize(TD_SC, "SC", None, TD_Sentinel_all, sourceFolder, prefix, outDF, i, nr_cores)
    #i = i + 1
# (2-8) Landsat_NONE_SENTINEL_CLEAN
    #prefix = "TC_L_NONE_S_CLEAN"
    #outDF = Parameterize(TD_TC, "TC", None, TD_Sentinel_clean, sourceFolder, prefix, outDF, i, nr_cores)
    #i = i + 1
    #prefix = "SC_L_NONE_S_CLEAN"
    #outDF = Parameterize(TD_SC, "SC", None, TD_Sentinel_clean, sourceFolder, prefix, outDF, i, nr_cores)
# (3) WRITE THE outDF TO DISK
    outDF.to_csv(sourceFolder + "_CV-results_and_parameters_20171214_short.csv", sep=",")
# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
    print("")
    endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print("--------------------------------------------------------")
    print("--------------------------------------------------------")
    print("start: " + starttime)
    print("end: " + endtime)
    print("")