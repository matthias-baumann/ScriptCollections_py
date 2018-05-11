# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import baumiTools as bt
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ####################################### FUNCTIONS, FOLDER PATHS AND BASIC VARIABLES ######################### #
inIMG = "G:/CHACO/_ANALYSES/LandUseChange_1985-2000-2013/map.tif"
outSieve = "B:/Projects-and-Publications/Projects_Active/_PASANOA/baumann-etal_LandCoverMaps/baumann_etal_2017_ChacoPLUS_LCC_allClasses_85_00_13.img"
# #### (1) Clunmp-Sieve the image
print("Do clump/sieve")
clumpSieve = bt.baumiRT.ClumpEliminate(inIMG, 8, 3)
# #### (2) WRITE OUTPUTS
print("Write Outputs")
bt.baumiRT.CopyMEMtoDisk(clumpSieve, outSieve)

# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")