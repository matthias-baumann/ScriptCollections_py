###################################################################
##### RF model training and image classification using sklearn for large areas
##### philippe.rufin@geo.hu-berlin.de

import datetime
import numpy
import gdal
import ogr
from scipy.stats import itemfreq
from sklearn.ensemble import RandomForestClassifier

###################################################################
##### PBC raster stacks
print('Opening PBC datasets')
PBC_DOY132 = gdal.Open('M:/LandsatData/Landsat_Turkey/02_OutputData/PBC_DOY_132.vrt')
PBC_DOY213 = gdal.Open('M:/LandsatData/Landsat_Turkey/02_OutputData/PBC_DOY_213.vrt')
PBC_DOY258 = gdal.Open('M:/LandsatData/Landsat_Turkey/02_OutputData/PBC_DOY_258.vrt')

###################################################################
##### PBC metrics & flags
print('Opening metric and flag datasets')
PBC_METRICS = gdal.Open('M:/LandsatData/Landsat_Turkey/02_OutputData/PBC_metrics.vrt')
PBC_DER_METRICS = gdal.Open('M:/LandsatData/Landsat_Turkey/02_OutputData/PBC_DerivedMetrics.vrt')
PBC_FLAGS = gdal.Open('M:/LandsatData/Landsat_Turkey/02_OutputData/PBC_flags.vrt')

###################################################################
##### SRTM 1 arc sec raster
print('Opening SRTM and slope datasets')
SRTM_ELEV = gdal.Open('Y:/DAR_Data/01_Processing/Processed_Data/SRTM_1arc_v3/SRTM_1arcv3_EPSG_3035_EXTENT.tif')
SRTM_SLOPE = gdal.Open('Y:/DAR_Data/01_Processing/Processed_Data/SRTM_1arc_v3/SRTM_1arcv3_SLOPE_EPSG_3035_EXTENT.tif')


###################################################################
#### Build empty raster for point based on the PBC extent & projection
PROJ = PBC_DOY132.GetProjection()
GT = PBC_DOY132.GetGeoTransform()

cols = PBC_DOY132.RasterXSize
rows = PBC_DOY132.RasterYSize
print('Raster dimensions - Cols: ' + str(cols) + ' rows: ' + str(rows))

TRAIN_POLY = ogr.Open('Y:/DAR_Data/01_Processing/Processed_Data/Training_Data/py/Training_Polygons_ETRS_3035.shp')
TRAIN_LYR = TRAIN_POLY.GetLayer(0)

drvMemR = gdal.GetDriverByName('MEM')
TRAIN_RASTER = drvMemR.Create('', cols, rows, 1, gdal.GDT_Int16)
TRAIN_RASTER.SetProjection(PROJ)
TRAIN_RASTER.SetGeoTransform(GT)

###################################################################
#### Write raster with training data
print('Rasterizing training polygons...')
gdal.RasterizeLayer(TRAIN_RASTER, [1], TRAIN_LYR, options = ["ALL_TOUCHED=FALSE", "ATTRIBUTE=LULC"])
print('Writing training raster...')
driver = gdal.GetDriverByName("GTiff")
copy_ds = driver.CreateCopy('Y:/DAR_Data/01_Processing/Processed_Data/Training_Data/py/Training_EPSG_3035_LULC.tif', TRAIN_RASTER, 0)
print('Writing training raster done')
copy_ds = None



###################################################################
##### Index training data to extract from input data
TRAINING = gdal.Open('Y:/DAR_Data/01_Processing/Processed_Data/Training_Data/py/Training_EPSG_3035_LULC.tif')
TRAINING_NP = TRAINING.ReadAsArray()
is_train = numpy.nonzero(TRAINING_NP)

TRAINING_LABELS = TRAINING_NP[is_train]
TRAINING_LABELS = numpy.hstack(TRAINING_LABELS)
TRAINING_LABELS = TRAINING_LABELS.reshape(len(TRAINING_LABELS), 1)


###################################################################
##### Convert input dataset into numpy array (pixel-based since reading the whole stuff takes forever)
INPUT_DATA_PBC132 = []
INPUT_DATA_PBC213 = []
INPUT_DATA_PBC258 = []
INPUT_DATA_PBC_METRICS = []
INPUT_DATA_PBC_DER_METRICS = [
]
INPUT_DATA_PBC_FLAGS = []
INPUT_DATA_SRTM_ELEV = []
INPUT_DATA_SRTM_SLOPE = []

for i in range(len(is_train[1])):
    y = is_train[0][i]
    x = is_train[1][i]
    INPUT_DATA_PBC132.append(PBC_DOY132.ReadAsArray(xoff=int(x), yoff=int(y), xsize=1, ysize=1))
    INPUT_DATA_PBC213.append(PBC_DOY213.ReadAsArray(xoff=int(x), yoff=int(y), xsize=1, ysize=1))
    INPUT_DATA_PBC258.append(PBC_DOY258.ReadAsArray(xoff=int(x), yoff=int(y), xsize=1, ysize=1))
    INPUT_DATA_PBC_METRICS.append(PBC_METRICS.ReadAsArray(xoff=int(x), yoff=int(y), xsize=1, ysize=1))
    INPUT_DATA_PBC_DER_METRICS.append(PBC_DER_METRICS.ReadAsArray(xoff=int(x), yoff=int(y), xsize=1, ysize=1))
    INPUT_DATA_PBC_FLAGS.append(PBC_FLAGS.ReadAsArray(xoff=int(x), yoff=int(y), xsize=1, ysize=1))
    INPUT_DATA_SRTM_ELEV.append(SRTM_ELEV.ReadAsArray(xoff=int(x), yoff=int(y), xsize=1, ysize=1))
    INPUT_DATA_SRTM_SLOPE.append(SRTM_SLOPE.ReadAsArray(xoff=int(x), yoff=int(y), xsize=1, ysize=1))
    print(i/len(is_train[1]))



###################################################################
##### Reshape and concatenate all the input stuff
INPUT_DATA_TOTAL = numpy.concatenate((INPUT_DATA_PBC132, INPUT_DATA_PBC213, INPUT_DATA_PBC258, INPUT_DATA_PBC_METRICS, INPUT_DATA_PBC_DER_METRICS, INPUT_DATA_PBC_FLAGS, INPUT_DATA_SRTM_ELEV, INPUT_DATA_SRTM_SLOPE), 1)
INPUT_DATA_HSTACK = numpy.hstack(INPUT_DATA_TOTAL)
INPUT_DATA_TSTACK = numpy.transpose(INPUT_DATA_HSTACK, (1,0,2))
rows, cols, n_bands = INPUT_DATA_TSTACK.shape
print(rows, cols, n_bands)

INPUT_DATA_TSTACK = INPUT_DATA_TSTACK.reshape(rows, cols)
TRAINING_FEATURES = INPUT_DATA_TSTACK



###################################################################
##### Backup that training data shabaam
numpy.save('Y:/DAR_Data/01_Processing/Processed_Data/Training_Data/py/TRAINING_FEATURES.npy', TRAINING_FEATURES)
numpy.save('Y:/DAR_Data/01_Processing/Processed_Data/Training_Data/py/TRAINING_LABELS.npy', TRAINING_LABELS)

TRAINING_LABELS = numpy.load('Y:/DAR_Data/01_Processing/Processed_Data/Training_Data/py/TRAINING_LABELS.npy')
TRAINING_FEATURES = numpy.load('Y:/DAR_Data/01_Processing/Processed_Data/Training_Data/py/TRAINING_FEATURES.npy')



###################################################################
##### Stratified equalized sample from the entire training dataset
STRAT_EQ_SAMPLE = []
for cl in numpy.unique(TRAINING_LABELS):
    is_class = numpy.where(TRAINING_LABELS == cl)
    len(is_class[0])
    STRAT_EQ_SAMPLE.append(numpy.random.choice(is_class[0], 700, replace = False))

STRAT_EQ_SAMPLE = numpy.hstack(STRAT_EQ_SAMPLE)
TRAINING_FEATURES_SAMPLE = TRAINING_FEATURES[STRAT_EQ_SAMPLE]
TRAINING_LABEL_SAMPLE = TRAINING_LABELS[STRAT_EQ_SAMPLE]

itemfreq(TRAINING_LABEL_SAMPLE)


###################################################################
##### Train RF model
RFM = RandomForestClassifier(n_estimators = 500, oob_score = True, n_jobs = 12)
RFmodel = RFM.fit(TRAINING_FEATURES_SAMPLE, TRAINING_LABEL_SAMPLE, sample_weight=None)
print(RFmodel.oob_score_*100)
print(RFmodel.feature_importances_)


###################################################################
##### Set up output raster for RF model prediction
PROJ = PBC_DOY132.GetProjection()
GT = PBC_DOY132.GetGeoTransform()

ySize = PBC_DOY132.RasterYSize
xSize = PBC_DOY132.RasterXSize

drvMemR = gdal.GetDriverByName('MEM')
mem_ds = drvMemR.Create('', xSize, ySize, 1, gdal.GDT_Byte)
mem_ds.SetGeoTransform(GT)
mem_ds.SetProjection(PROJ)


###################################################################
##### Initiate block-wise RF model prediction
xBlockSize = int(xSize / 100)
yBlockSize = int(ySize / 100)
i = 0

for row in range(0, ySize, yBlockSize):
    for col in range(0, xSize, xBlockSize):

        i += 1
        print("Reading input feature block " + str(i) + " of " + str(int((xSize * ySize) / (xBlockSize * yBlockSize))))
        PBC_DOY132_CHIP = PBC_DOY132.ReadAsArray(col, row, xBlockSize, yBlockSize)
        PBC_DOY213_CHIP = PBC_DOY213.ReadAsArray(col, row, xBlockSize, yBlockSize)
        PBC_DOY258_CHIP = PBC_DOY258.ReadAsArray(col, row, xBlockSize, yBlockSize)
        PBC_METRICS_CHIP = PBC_METRICS.ReadAsArray(col, row, xBlockSize, yBlockSize)
        PBC_DER_METRICS_CHIP = PBC_DER_METRICS.ReadAsArray(col, row, xBlockSize, yBlockSize)
        PBC_FLAGS_CHIP = PBC_FLAGS.ReadAsArray(col, row, xBlockSize, yBlockSize)

        PREDICT_CHIP = numpy.concatenate((PBC_DOY132_CHIP, PBC_DOY213_CHIP, PBC_DOY258_CHIP, PBC_METRICS_CHIP, PBC_DER_METRICS_CHIP, PBC_FLAGS_CHIP), 0)
        PREDICT_CHIP = PREDICT_CHIP.transpose(1,2,0)
        rows, cols, n_bands = PREDICT_CHIP.shape

        if numpy.count_nonzero(PREDICT_CHIP) > 0:
            print('Block contains data - predicting...')
            n_samples = rows*cols
            FLAT_INPUT = PREDICT_CHIP.reshape((n_samples, n_bands))
            RESULT = RFmodel.predict(FLAT_INPUT)
            CLASSIFICATION_CHIP = RESULT.reshape((rows, cols))

            print('Writing output to band')
            mem_ds.GetRasterBand(1).WriteArray(CLASSIFICATION_CHIP, col, row)

driver = gdal.GetDriverByName("GTiff")
copy_ds = driver.CreateCopy('Y:/DAR_Data/01_Processing/Processed_Data/Training_Data/py/classification_LULC.tif', mem_ds, 0)
copy_ds = None

datetime.datetime.now()