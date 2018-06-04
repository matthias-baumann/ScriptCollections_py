import baumiTools as bt


infile = "L:/_SHARED_DATA/ASP_MB/LC2015/Run03_clumpEliminate_crop_2015"
cl = bt.baumiRT.ClumpEliminate(infile + ".tif", 8, 8)
bt.baumiRT.CopyMEMtoDisk(cl, infile + "_8px.tif")