

import ogr, gdal, osr
import baumiTools as bt

minWild = gdal.Open("Y:/Baumann/BALTRAK/Connectivity/03_Layer-MIN/MIN_Wilderness_1990.tif")

conn = gdal.Open("Y:/Baumann/BALTRAK/Connectivity/Results/Buffer_removed_NAs/Normalized/MIN_Wilderness_1990_60_nodes_50_cum_curmap_nobuff_noNA_normalized.tif")

print(minWild.GetProjection())
print(conn.GetProjection())

exit(0)
minWild.SetProjection(conn.GetProjection())

minWild = None
