import os
import time
import shutil
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ####################################### GLOBAL FUNCTIONS #################################################### #

# ####################################### START PROCESSING #################################################### #
in_root = "H:/Baltrak/01_PreProcessing/02_ReProjected_Scenes_L8/"

# (1) Get files in in_root, start loop
fileList = os.listdir(in_root)
for item in fileList:
    sceneList = os.listdir(in_root + "/" + item)
    for scene in sceneList:
        # Create bandlist
        bandList = os.listdir(in_root + item +"/" + scene + "/")
        # find .xml and .txt file
        xmlFile = [a for a in bandList if a.startswith('LC8') and a.endswith('.xml')]
        txtFile = [a for a in bandList if a.startswith('LC8') and a.endswith('.txt')]
        # create inpath
        inpath = in_root + item +"/" + scene + "/"
        #create output filenameroot
        outFileNameRoot = bandList[0]
        # rename .xml and .txt file
        shutil.move(inpath + txtFile[0], inpath + outFileNameRoot[:-4] + "_MTL.txt")
        shutil.move(inpath + xmlFile[0], inpath + outFileNameRoot[:-4] + ".xml")


# ####################################### END-OF-SCRIPT-PRINTING ############################################# #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: ", starttime)
print("end: ", endtime)
print("")