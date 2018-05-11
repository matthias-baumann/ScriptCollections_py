# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import os
import time, datetime
import tarfile
from multiprocessing import Pool
import shutil

# ############################################################################################################# #
def main():
# ####################################### SET TIME-COUNT ###################################################### #
    starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print("--------------------------------------------------------")
    print("Starting process, time:" +  starttime)
    print("")
# ####################################### HARD-CODED FOLDER PATHS ############################################# #
    FP_Folder = "O:/Santos_BadgerPhenology_Landsat/"
    out_folder = "O:/Zipped/"
# BUILD FILE PATHS
    pathList = []
    FPs = [file for file in os.listdir(FP_Folder)]
    for fp in FPs:
        scenes = [sc for sc in os.listdir(FP_Folder+fp+"/")]
        for scene in scenes:
            infolder = FP_Folder + fp + "/" + scene + "/"
            outtar = out_folder + fp + "/" + scene + ".tar.gz"
            pathList.append([infolder,outtar])
    pool = Pool(processes=8)
    pool. map(WorkerFunction, pathList)
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

def WorkerFunction(list):

# ####################################### GLOBAL FUNCTION ##################################################### #
    def tar_gz(in_folder, out_file):
        fileList = os.listdir(in_folder)
        selection = ["lndsr", "fmask", "GCP", "MTL", "metadata"]
        # Only compress files that match the selection-criteria
        tar = tarfile.open(out_file, "w:gz")
        for file in fileList:
            if any(sel in file for sel in selection):
                compr = in_folder + file
                tar.add(compr, arcname = file)
        tar.close()
    # ZIP
    in_folder = list[0]
    outtar = list[1]
    print(outtar)
    tar_gz(in_folder, outtar)
    # REMOVE LEDAPS-FMASK FOLDER FROM DISK
    print("Remove LEDAPS/Fmask output, " + in_folder)
    shutil.rmtree(in_folder)


if __name__ == "__main__":
    main()

