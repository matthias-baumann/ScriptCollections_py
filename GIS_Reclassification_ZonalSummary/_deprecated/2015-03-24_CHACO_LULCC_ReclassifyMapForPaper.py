import time
import baumiTools as bt
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ####################################### DEFINE WORK-FOLDERS AND FILES ####################################### #
work_Folder = "F:/Projects-and-Publications/Projects_Active/_PASANOA/baumann-etal_LandCoverMaps/"
input_raster = work_Folder + "baumann_etal_2017_ChacoOnly_LCC_allClasses_85_00_13.img"
# ####################################### PROCESSING ########################################################## #
# 1985
cc_85 = [[0,0],[1,1],[2,2],[3,3],[4,4],[5,5],[6,6],[7,7],[8,8],[9,9],[10,1],
		 [11,1],[12,1],[13,1],[14,1],[15,2],[16,4],[17,17],[18,3],[19,3],[20,5],
		 [21,5],[22,2],[23,2]]
reclass85 = bt.baumiRT.ReclassifyRaster(input_raster, cc_85)
bt.baumiRT.CopyMEMtoDisk(reclass85, work_Folder + "CHACO_LC1985.tif")
# 2000
cc_00 = [[0,0],[1,1],[2,2],[3,3],[4,4],[5,5],[6,6],[7,7],[8,8],[9,9],[10,4],
		 [11,5],[12,1],[13,1],[14,5],[15,2],[16,99],[17,17],[18,5],[19,3],[20,4],
		 [21,5],[22,4],[23,2]]
reclass00 = bt.baumiRT.ReclassifyRaster(input_raster, cc_00)
bt.baumiRT.CopyMEMtoDisk(reclass00, work_Folder + "CHACO_LC2000.tif")
# 2013
cc_13 = [[0,0],[1,1],[2,2],[3,3],[4,4],[5,5],[6,6],[7,7],[8,8],[9,9],[10,4],
		 [11,5],[12,4],[13,5],[14,5],[15,2],[16,99],[17,17],[18,5],[19,5],[20,4],
		 [21,4],[22,4],[23,4]]
reclass13 = bt.baumiRT.ReclassifyRaster(input_raster, cc_13)
bt.baumiRT.CopyMEMtoDisk(reclass13, work_Folder + "CHACO_LC2013.tif")



# ####################################### END TIME-COUNT ###################################################### #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: ", starttime)
print("end: ", endtime)
print("")