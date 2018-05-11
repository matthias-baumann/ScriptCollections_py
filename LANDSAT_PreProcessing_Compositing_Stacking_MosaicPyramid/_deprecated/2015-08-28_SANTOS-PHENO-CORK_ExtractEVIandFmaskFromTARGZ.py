# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import os
import time
from ZumbaTools.FileManagement_Tools import *
from ZumbaTools.Raster_Tools import *
import tarfile
from multiprocessing import Pool
import gdal
import numpy as np
from gdalconst import *
# ####################################### PROCESSING ########################################################## #
def main():
# ####################################### SET TIME-COUNT ###################################################### #
    starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print("--------------------------------------------------------")
    print("Starting process, time:" +  starttime)
    print("")
    # ####################################### GLOBAL DEFINITIONS ################################################## #
    #input_folder = "L:/South_America/Personal_Folders/Baumann/tep/"
    input_folder = "R:/South_America/Personal_Folders/Baumann/Neuer Ordner/"
    #fileList = [input_folder + file for file in os.listdir(input_folder) if file.endswith("tar.gz")]
    fileList = [input_folder + file for file in os.listdir(input_folder) if file.endswith("tar.gz") and file.find("LC") < 0]

    pool = Pool(processes=5)
    pool.map(WorkerFunction_L57, fileList)
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

def WorkerFunction_L57(scenePaths):
    output_root = "O:/Santos_BadgerPhenology_Landsat_evi-create/"
    file = scenePaths
    print(file)
# Create output-path
    p1 = file.rfind("/")
    p2 = file.find(".tar.gz")
    outPath = output_root + file[p1+1:p2] + "/"
    CreateFolder(outPath)
# # Open the tar-gz and extract
    tar = tarfile.open(file, "r")
    list = tar.getnames()
    for f in list:
        if f.find("cfmask.tif")>= 0 or f.find("band1.tif") >= 0 or f.find("band3.tif") >= 0 or f.find("band4.tif") >= 0:
            tar.extractall(outPath, members=[tar.getmember(f)])
    tar.close()
    outDrv = gdal.GetDriverByName('GTiff')
# # Calculate EVI, mask out clouds, and write both files to disk
    b1 = OpenRasterToMemory([(outPath +  b) for b in os.listdir(outPath) if b.endswith("band1.tif")][0])
    b3 = OpenRasterToMemory([(outPath + "/" + b) for b in os.listdir(outPath) if b.endswith("band3.tif")][0])
    b4 = OpenRasterToMemory([(outPath + "/" + b) for b in os.listdir(outPath) if b.endswith("band4.tif")][0])
    mask = OpenRasterToMemory([(outPath + "/" + b) for b in os.listdir(outPath) if b.endswith("cfmask.tif")][0])
    cols = b1.RasterXSize
    rows = b1.RasterYSize
    pr = b1.GetProjection()
    gt = b1.GetGeoTransform()
    b1_rb = b1.GetRasterBand(1).ReadAsArray(0,0,cols,rows)/10000
    b3_rb = b3.GetRasterBand(1).ReadAsArray(0,0,cols,rows)/10000
    b4_rb = b4.GetRasterBand(1).ReadAsArray(0,0,cols,rows)/10000
    mask_rb = mask.GetRasterBand(1).ReadAsArray(0,0,cols,rows)
    evi = 2.5 * (b4_rb - b3_rb) / (b4_rb + 6*b3_rb - 7.5*b1_rb + 1)
    dataOut = evi
    np.putmask(dataOut, mask_rb != 0, 0)
    #np.putmask(dataOut, dataOut < 0, 0)
    outName = [(outPath +  b) for b in os.listdir(outPath) if b.endswith("band1.tif")][0]
    outName = outName.replace("band1.tif", "evi.tif")
    outFile = outDrv.Create(outName, cols, rows, 1, GDT_Float32)
    outFile.SetProjection(pr)
    outFile.SetGeoTransform(gt)
    outFile.GetRasterBand(1).WriteArray(dataOut, 0, 0)
# Remove the band files
    os.remove([(outPath +  b) for b in os.listdir(outPath) if b.endswith("band1.tif")][0])
    os.remove([(outPath +  b) for b in os.listdir(outPath) if b.endswith("band3.tif")][0])
    os.remove([(outPath +  b) for b in os.listdir(outPath) if b.endswith("band4.tif")][0])
    b1 = None
    b3 = None
    b4 = None
    mask = None
    b1_rb = None
    b3_rb = None
    b4_rb = None
    mask_rb = None
    evi = None
    outFile = None



def WorkerFunction_L8(sceneID):
    output_root = "O:/Santos_BadgerPhenology_Landsat_evi-create/"
    evi_root = "L:/South_America/Personal_Folders/Baumann/L8evi/"
    cfmask_root = "L:/South_America/Personal_Folders/Baumann/L8/"
    file = sceneID
    print(file)
# Create output-path
    p2 = file.rfind("-")
    outPath = output_root + file[:p2]
    CreateFolder(outPath)
# Open the tar-gz and extract
    eviPath = [evi_root + subscr for subscr in os.listdir(evi_root) if subscr.find(file[:p2]) >=0 ][0]
    # EVI-File
    tar = tarfile.open(eviPath, "r")
    list = tar.getnames()
    for f in list:
        if f.find("evi.tif") >= 0:
            tar.extractall(outPath, members=[tar.getmember(f)])
    tar.close()
    # Cfmask
    cfMaskPath = [cfmask_root + subscr for subscr in os.listdir(cfmask_root) if subscr.find(file[:p2]) >=0 ][0]
    tar = tarfile.open(cfMaskPath, "r")
    list = tar.getnames()
    for f in list:
        if f.find("cfmask.tif") >= 0:
            tar.extractall(outPath, members=[tar.getmember(f)])
    tar.close()




if __name__ == "__main__":
    main()