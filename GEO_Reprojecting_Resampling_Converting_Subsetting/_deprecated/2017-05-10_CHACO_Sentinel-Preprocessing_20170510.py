# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
#from snappy import jpy
from snappy import ProductIO
from snappy import GPF
from snappy import HashMap
#import numpy as np
#import gdal, ogr, osr
import os, time
#import baumiTools as bt
from joblib import Parallel, delayed
import multiprocessing
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " + starttime)
print("")
# ####################################### FILES, FOLDER-PATHS AND PROCESSING DEFINITIONS ###################### #
inFolder = "G:/CHACO/ReprojectedScenes/S1_Download_new/Batch05/"#Batch02
outFolder_VH = "G:/CHACO/ReprojectedScenes/S1_Preprocessed/VH/"
outFolder_VV = "G:/CHACO/ReprojectedScenes/S1_Preprocessed/VV/"
# ####################################### FUNCTIONS ########################################################### #
def readMetadata(sentinel_1_path, toPrint=True):
    # Extract information about the Sentinel-1 GRD product:
    # sentinel_1_metadata = "manifest.safe"
    # s1prd = "data/%s/%s.SAFE/%s" % (sentinel_1_path, sentinel_1_path, sentinel_1_metadata)
    s1prd = sentinel_1_path + "/" + [folder for folder in os.listdir(sentinel_1_path)][0] + "/manifest.safe"
    reader = ProductIO.getProductReader("SENTINEL-1")
    product = reader.readProductNodes(s1prd, None)
    width = product.getSceneRasterWidth()
    height = product.getSceneRasterHeight()
    name = product.getName()
    band_names = product.getBandNames()
    #if toPrint:
    #    print("Product: %s, %d x %d pixels" % (name, width, height))
    #   print("Bands:   %s" % (list(band_names)))
    return product
def radiometricCalibration(img, polarization):
    parameters = HashMap()
    parameters.put('auxFile', 'Latest Auxiliary File')
    parameters.put('outputSigmaBand', True)
    parameters.put('selectedPolarisations', polarization)
    calibrate = GPF.createProduct('Calibration', parameters, img)
    #list(calibrate.getBandNames())
    return calibrate
def speckleFiltering(calibrate, toPrint=True):
    parameters = HashMap()
    parameters.put('filter', 'Lee')
    parameters.put('filterSizeX', 7)
    parameters.put('filterSizeY', 7)
    parameters.put('dampingFactor', 2)
    parameters.put('edgeThreshold', 5000.0)
    parameters.put('estimateENL', True)
    parameters.put('enl', 1.0)
    speckle = GPF.createProduct('Speckle-Filter', parameters, calibrate)
    band_names = speckle.getBandNames()
    #if toPrint:
    #    print(list(band_names))
    return speckle
def terrainCorrection(speckle, toPrint=True):
    parameters = HashMap()
    srtm = "G:/CHACO/SRTM_30m_ChacoPlus_TIFF.tif"
    # parameters.put('demName', 'SRTM 3Sec')
    parameters.put('externalDEMfile', srtm)
    parameters.put('externalDEMNoDataValue', -32767.0)
    # parameters.put('demResamplingMethod', "BILINEAR_INTERPOLATION")
    # parameters.put('imgResamplingMethod', "BILINEAR_INTERPOLATION")
    parameters.put('demResamplingMethod', "CUBIC_CONVOLUTION")
    parameters.put('imgResamplingMethod', "CUBIC_CONVOLUTION")
    parameters.put('pixelSpacingInMeter', 30.0)
    # parameters.put('pixelSpacingInDegree', 0.0)
    parameters.put('mapProjection', "WGS84(DD)")
    # parameters.put('mapProjection', 'EPSG:102033')
    terrain = GPF.createProduct('Terrain-Correction', parameters, speckle)
    #if toPrint:
    #    print("Bands:   %s" % (list(terrain.getBandNames())))
    return terrain
def OrbitFileApplication(readFile):
    parameters = HashMap()
    # sources = HashMap()
    parameters.put('orbitType', "Sentinel Precise (Auto Download)")
    parameters.put('PolyDegree', 3)
    parameters.put('continueOnFail', True)
    item = GPF.createProduct("Apply-Orbit-File", parameters, readFile)
    return item
# ####################################### BUILD JOB-LIST ###################################################### #
workList = []
sceneList = [scenes for scenes in os.listdir(inFolder) if not scenes.startswith("_RawDownload")]
for scene in sceneList:
    task = [inFolder, scene, outFolder_VH, outFolder_VV]
    workList.append(task)
# ####################################### LOOP THROUGH JOBS ###################################################### #
for job in workList:
# ####################################### EXTRACT ITEMS FROM LIST ############################################# #
    inFolder = job[0]
    inFile = job[1]
    outFolder_VH = job[2]
    outFolder_VV = job[3]
# ####################################### START THE JOBS --> VH and VV ######################################## #
    print(inFile)
    inputPath = inFolder + inFile
    # VV
    print("VV")
    out_VV = outFolder_VV + inFile + ".tif"
    if not os.path.exists(out_VV):
        product = readMetadata(inputPath, toPrint=True)
        productOFA = OrbitFileApplication(product)
        radioCorrect = radiometricCalibration(productOFA, 'VV')
        sF = speckleFiltering(radioCorrect, toPrint=True)
        geoCorr = terrainCorrection(sF, toPrint=True)
        ProductIO.writeProduct(geoCorr, out_VV, 'GeoTIFF')
    # VH
    print("VH")
    out_VH = outFolder_VH + inFile + ".tif"
    if not os.path.exists(out_VH):
        product = readMetadata(inputPath, toPrint=True)
        productOFA = OrbitFileApplication(product)
        radioCorrect = radiometricCalibration(productOFA, 'VH')
        sF = speckleFiltering(radioCorrect, toPrint=True)
        geoCorr = terrainCorrection(sF, toPrint=True)
        ProductIO.writeProduct(geoCorr, out_VH, 'GeoTIFF')
# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")




exit(0)

starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
exit(0)
GPF.getDefaultInstance().getOperatorSpiRegistry().loadOperatorSpis()
HashMap = snappy.jpy.get_type('java.util.HashMap')
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " +  starttime)
print("")
# ####################################### DRIVERS AND FOLDER-PATHS ############################################ #








path = "F:/S1B_IW_GRDH_1SDV_20161226T092902_20161226T092927_003565_006196_390F/"

for folder in os.listdir(path):

    scene = path + folder + "/"
    print(scene)

    timestamp = folder.split("_")[4]
    date = timestamp[:8]
    print(date)

    sentinel_1 = ProductIO.readProduct(scene + "/manifest.safe")

    for p in ['VH', 'VV']:
        ## Calibration
        polarization = p
        parameters = HashMap()
        parameters.put('outputSigmaBand', True)
        parameters.put('sourceBands', 'Intensity_' + polarization)
        parameters.put('selectedPolarisations', polarization)
        parameters.put('outputImageScaleInDb', False)

        calib = scene + date + "_calibrate_" + polarization
        target_0 = GPF.createProduct("Calibration", parameters, sentinel_1)
        ProductIO.writeProduct(target_0, calib, 'BEAM-DIMAP')

        ## Terrain correction
        params = HashMap()
        params.put('demResamplingMethod', 'NEAREST_NEIGHBOUR')
        params.put('imgResamplingMethod', 'NEAREST_NEIGHBOUR')
        params.put('demName', 'SRTM 3Sec')
        params.put('pixelSpacingInMeter', 10.0)
        params.put('sourceBands', 'Sigma0_' + polarization)

        terrain = scene + date + "_corrected_" + polarization
        target_2 = GPF.createProduct("Terrain-Correction", params, target_0)
        ProductIO.writeProduct(target_2, terrain, 'GeoTIFF')

        endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
        print("start: " + starttime)
        print("end: " + endtime)



        exit(0)

