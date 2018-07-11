import gdal
import numpy as np
ds = gdal.Open("Y:/Baumann/_ANALYSES/PercentTreeCover/___MaskedProducts/TC_Landsat-Sentinel.tif")
arr = ds.GetRasterBand(1).ReadAsArray(0, 0, ds.RasterXSize, ds.RasterYSize)

median = np.median(arr)
mean = np.mean(arr)
sd = np.std(arr)
upper_quartile = np.percentile(arr, 75)
lower_quartile = np.percentile(arr, 25)

iqr = upper_quartile - lower_quartile
upper_whisker = arr[arr<=upper_quartile+1.5*iqr].max()
lower_whisker = arr[arr>=lower_quartile-1.5*iqr].min()

print("Median:", median)
print("Upper quartile:", upper_quartile)
print("Lower quartile:", lower_quartile)
print("Upper Whisker:", upper_whisker)
print("Lower Whisker:", lower_whisker)
print("mean:", mean)
print("sd:", sd)