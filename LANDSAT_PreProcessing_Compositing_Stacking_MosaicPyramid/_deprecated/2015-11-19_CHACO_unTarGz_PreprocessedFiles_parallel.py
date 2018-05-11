# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import os
import time
from multiprocessing import Pool
from ZumbaTools.FileManagement_Tools import *

# ############################################################################################################# #
def main():
# ####################################### SET TIME-COUNT ###################################################### #
    starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print("--------------------------------------------------------")
    print("Starting process, time:" +  starttime)
    print("")
# ####################################### FOOTPRINTS ########################################################## #
    # Get number of footprints
    FP_Folder = "G:/CHACO/ReprojectedScenes_zipped/"
    FPs = []
    list = os.listdir(FP_Folder)
    for folder in list:
        FPs.append(folder)

    pool = Pool(processes=40)
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
    out_folder = "G:/CHACO/ReprojectedScenes/Landsat457/"
    in_folder = "G:/CHACO/ReprojectedScenes_zipped/"
# ####################################### PROCESSING ########################################################## #
    workfolder = in_folder + Footprints + "/"
    # #### (1) WITHIN FP-FOLDER LIST SCENE-IDs, THEN LOOP ####
    sceneList = os.listdir(workfolder)
    for scene in sceneList:
        print(scene)
    # Define input
        intargz = workfolder + scene
    # Build output-folder
        FP_out = out_folder + Footprints + "/"
        if not os.path.exists(FP_out):
            os.makedirs(FP_out)
        scene_out = FP_out + scene
        scene_out = scene_out.replace(".tar.gz", "")
        if not os.path.exists(scene_out):
            os.makedirs(scene_out)
        UnTarGZ(intargz, scene_out)


if __name__ == "__main__":
    main()

