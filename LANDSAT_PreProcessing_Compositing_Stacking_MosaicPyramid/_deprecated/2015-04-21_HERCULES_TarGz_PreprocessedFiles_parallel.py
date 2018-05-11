# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import os
import time
from multiprocessing import Pool
from ZumbaTools.FileManagement_Tools import *
import shutil

# ############################################################################################################# #
def main():
# ####################################### SET TIME-COUNT ###################################################### #
    starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print("--------------------------------------------------------")
    print("Starting process, time:" +  starttime)
    print("")
# ####################################### FOOTPRINTS ########################################################## #
    # Get number of footprints
    FP_Folder = "G:/HERCULES/01_PreProcessing/02_ReProjected_Scenes/"
    FPs = []
    list = os.listdir(FP_Folder)
    for folder in list:
        FPs.append(folder)

    pool = Pool(processes=25)
    pool. map(WorkerFunction, FPs)
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

def WorkerFunction(Footprints):
# ####################################### HARD-CODED FOLDER PATHS ############################################# #
    FP_Folder = "G:/HERCULES/01_PreProcessing/02_ReProjected_Scenes/"
    out_folder = "G:/HERCULES/01_PreProcessing/02_ReProjected_Scenes_zipped/"
# ####################################### PROCESSING ########################################################## #
    workfolder = FP_Folder + Footprints + "/"
    # #### (1) WITHIN FP-FOLDER LIST SCENE-IDs, THEN LOOP ####
    sceneList = os.listdir(workfolder)
    for scene in sceneList:
        print(scene)
        sceneFolder = workfolder + scene + "/"
    # #### (2) CHECK IF MAIN-FOLDER (FOOTPRINT-FOLDER) EXISTS, OTHERWISE CREATE
        fp_folder = out_folder + Footprints + "/"
        if not os.path.exists(fp_folder):
            os.makedirs(fp_folder)
    # #### (3) tar.gz AND MOVE
        storeFile = fp_folder + scene + ".tar.gz"
        if not os.path.exists(storeFile):
            TarGZ(sceneFolder, storeFile, [])
        else:
            print("Already processed. Skipping...")
    # #### (4) DELETE THE FILES IN THE INPUT-FOLDER
        shutil.rmtree(sceneFolder)

if __name__ == "__main__":
    main()

