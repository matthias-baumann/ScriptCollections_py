# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time, os
from multiprocessing import Pool

def main():
    # ####################################### SET TIME-COUNT ###################################################### #
    starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print("--------------------------------------------------------")
    print("Starting process, time:" + starttime)
    print("")
    # ####################################### FUNCTIONS, FOLDER PATHS AND BASIC VARIABLES ######################### #
    root_folder_IN = "G:/BALTRAK/00_StackedTiles/"
    out_folder = "G:/BALTRAK/00_StackedTiles02/"
    # ####################################### PROCESSING ########################################################## #
    # (1) GET LISTS OF TILES FOR THE YEARS WE WANT TO STACK
    # Take the first folder to create the index
    list = [input for input in os.listdir(root_folder_IN) if input.endswith('.bsq')]


    pool = Pool(processes=48)
    pool.map(WorkerFunction, list)
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

def WorkerFunction(List_of_Tiles):
    # ####################################### FOLDER PATHS AND BASIC VARIABLES ######################### #
    root_folder_IN = "G:/BALTRAK/00_StackedTiles/"
    out_folder = "G:/BALTRAK/00_StackedTiles02/"
    base = List_of_Tiles # changed the variable name into 'base' so that I don't have to chnge much code from the single processing
    bandsToSubset_9000 = list(range(1, 157))
    bandsToSubset_15 = list(range(235, 313))
    # ################################################################################################## #
    # Build the outputFileName
    infile = root_folder_IN + base
    outfile = out_folder + base
    command = "gdal_translate -q -of ENVI "
    for b in bandsToSubset_9000:
        command = command + "-b " + str(b) + " "
    for b2 in bandsToSubset_15:
        command = command + "-b " + str(b2) + " "
    command = command + infile + " " + outfile
    if not os.path.exists(outfile):
        print("start " + infile)
        os.system(command)
    else:
        print("--> Already processed. Skipping...")
    print("done " + infile)

if __name__ == "__main__":
    main()
