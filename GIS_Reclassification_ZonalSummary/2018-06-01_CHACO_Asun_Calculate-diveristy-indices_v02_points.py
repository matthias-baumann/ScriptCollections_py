# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import baumiTools as bt
import gdal, osr
import numpy as np
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time:" +  starttime)
print("")
# ####################################### FOLDER PATHS AND BASIC VARIABLES #################################### #
rootFolder = "Z:/_SHARED_DATA/ASP_MB/LC2015/"
drvMemR = gdal.GetDriverByName('MEM')
output = rootFolder + "_SHDI_20180604.csv"
# ####################################### FUNCTIONS ########################################################### #
def calcSHDI(array):
    arraySize = array.size
    SHDI = 0
    vals = [1, 2, 3, 5]
    array = np.where(array == 17, 1, array) # reclassify open woodlands into forest
    for val in vals:
        count = (array == val).sum()
        # Check if value in in there, if not (i.e., count=0) then skip, because otherwise the ln will not be calculated
        if count > 0:
            prop = count / arraySize
            SHDI = SHDI + (prop * np.log(prop))
        else:
            SHDI = SHDI
    SHDI = - SHDI
    return SHDI
def makeSlices(array, windowSize):
    # adopted from cgarrard, make later a function in btTools out of it
    # array : 2d array"
    # windowSize : size of the moving window --> in cgarrad cols/rows are different, here they are squared

    # Calculate the nr ofcolumns and rows
    rows = array.shape[0] - windowSize + 1
    cols = array.shape[1] - windowSize + 1
    # Create an empty list for the slices
    slices = []
    # Populate the list
    for i in range(windowSize):
        for j in range(windowSize):
            slices.append(array[i:rows+i, j:cols+j])
            #print(slices)
        #exit(0)
    slices = np.array(slices)
    return slices
# ####################################### START PROCESSING #################################################### #
# (1) Load image to memory, get infos from it
ds = gdal.Open(rootFolder + "Run03_clumpEliminate_crop_2015_8px.tif")
points = bt.baumiVT.CopyToMem("Z:/_SHARED_DATA/ASP_MB/cameras_diversity_index/cameras_juli_bibi_mica.shp")
gt = ds.GetGeoTransform()
pr = ds.GetProjection()
rb = ds.GetRasterBand(1)
# (2) Initialize output
outList = [["UniqueID", "SHDI_3000", "SHDI_5000"]]
# (3) Build coordinate transformation
lyr = points.GetLayer()
source_SR = lyr.GetSpatialRef()
target_SR = osr.SpatialReference()
target_SR.ImportFromWkt(pr)
coordTrans = osr.CoordinateTransformation(source_SR, target_SR)
# (4) loop through features
feat = lyr.GetNextFeature()
while feat:
# Initialize the output, get ID
    id = feat.GetField("UniqueID")
    print(id)
    vals = [id]
# Get geometry, translate into array coordinate
    geom = feat.GetGeometryRef()
    geom.Transform(coordTrans)
    mx, my = geom.GetX(), geom.GetY()
    #print(mx, my)
    px = int((mx - gt[0]) / gt[1])
    py = int((my - gt[3]) / gt[5])
    #print(px, py)
# Loop over the 100 cells
    vals_3000 = []
    vals_5000 = []
    for i in range(-5, 5, 1):
        for j in range(-5, 5, 1):
        # Define the pixel-coordinate for the cell
            center_x = px + i
            center_y = py + j
            #print(center_x, center_y)
        # Extract the arrays, and calculate SHDI
            # 3000m radius
            UL_x_3000 = center_x - 50
            UL_y_3000 = center_y - 50
            array_3000 = rb.ReadAsArray(UL_x_3000, UL_y_3000, 100, 100)
            SHDI_3000 = calcSHDI(array_3000)
            vals_3000.append(SHDI_3000)
        # 5000m radius
            UL_x_5000 = center_x - 83
            UL_y_5000 = center_y - 83
            array_5000 = rb.ReadAsArray(UL_x_5000, UL_y_5000, 166, 166)
            SHDI_5000 = calcSHDI(array_5000)
            vals_5000.append(SHDI_5000)
    # Calculate the means
    mean_3000 = sum(vals_3000)/len(vals_3000)
    mean_5000 = sum(vals_5000)/len(vals_5000)
    # Append to output, take next feature
    vals.append(SHDI_3000)
    vals.append(SHDI_5000)
    outList.append(vals)
    feat = lyr.GetNextFeature()
# Write output
bt.baumiFM.WriteListToCSV(output, outList, ",")
# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")