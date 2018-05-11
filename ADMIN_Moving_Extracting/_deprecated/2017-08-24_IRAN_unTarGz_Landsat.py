# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import os, time
import baumiTools as bt
from joblib import Parallel, delayed
# ####################################### FUNCTIONS ########################################################### #
def Unzip(inpath):
    print(inpath[0])
    bt.baumiFM.UnTarGZ(inpath[0], inpath[1])

# ####################################### START ############################################################### #
if __name__ == '__main__':
# ####################################### SET TIME COUNT ###################################################### #
    starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print("--------------------------------------------------------")
    print("Starting process, time:" +  starttime)
    print("")
# ####################################### FOLDER PATHS ######################################################## #
    inputFolder = "L:/_SHARED_DATA/HB_MB/Landsat/RAW/"
# ####################################### PROCESSING ########################################################## #
    processList = []
    fileList = bt.baumiFM.GetFilesInFolderWithEnding(inputFolder, ".tar.gz", True)
    for file in fileList:
        process = []
        process.append(file)
        outpath = file.replace("RAW/", "")
        outpath = outpath.replace(".tar.gz", "/")
        process.append(outpath)
        processList.append(process)

    Parallel(n_jobs=45)(delayed(Unzip)(i) for i in processList)

# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
    print("")
    endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print("--------------------------------------------------------")
    print("--------------------------------------------------------")
    print("start: " + starttime)
    print("end: " + endtime)
    print("")