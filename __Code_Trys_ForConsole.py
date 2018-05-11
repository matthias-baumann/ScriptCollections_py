import ogr
shp = ogr.Open(r'D:\Warfare\_SHPs\BIOMES_TropicsSavannas_10kmGrid_polygons_testsub.shp')

























areaCover = forest2000.multiply(ee.Image.pixelArea()).divide(10000).select([0],["areacover"])

areaLoss = lossImage.gt(0).multiply(ee.Image.pixelArea()).divide(10000).select([0],["arealoss"])
areaGain = gainImage.gt(0).multiply(ee.Image.pixelArea()).divide(10000).select([0],["areagain"])

total = gfc2016.addBands(areaCover).addBands(areaLoss).addBands(areaGain)

polSums = areaCover.reduceRegions(collection=featCol, reducer=ee.Reducer.sum(), scale=30)

def addVar(feature):

    nfeat = ee.Feature(ee.Feature(feature).geometry(), {})

    def addVarYear(year, feat):

        year = ee.Number(year).toInt()
        feat = ee.Feature(feat)

        actual_year = ee.Number(2000).add(year)

        filtered = total.select("lossyear").eq(year)
        filtered = total.updateMask(filtered)

        reduc = filtered.reduceRegion(geometry=feature.geometry(), reducer=ee.Reducer.sum(), scale=30, maxPixels=1e13)

        loss = ee.Number(reduc.get("arealoss"))
        gain = ee.Number(reduc.get("areagain"))
        nameloss = ee.String("loss_").cat(actual_year)
        namegain = ee.String("gain_").cat(actual_year)

        #cond = loss.gt(0).Or(gain.gt(0))
        return feat.set(nameloss, loss, namegain, gain)

        #return ee.Feature(feat.geometry(), {nameloss:loss, namegain:gain})

    newFeat = ee.Feature(years.iterate(addVarYear, nfeat))

    return newFeat

areas = polSums.map(addVar).toList()

print(areas.getInfo())

exit(0)



#print(CalcLoss(featCol).getInfo())


print("Extract values for points in SHP-file")
tupel = []
lyr = shp.GetLayer()
coord = lyr.GetSpatialRef()
nFeat = lyr.GetFeatureCount()
count = 1
# Build a corrdinate transformation
source_SR = lyr.GetSpatialRef()
target_SR = osr.SpatialReference()
target_SR.ImportFromEPSG(4326)
coordTrans = osr.CoordinateTransformation(source_SR, target_SR)
# Get Point-ID from shapefile
polList = []

feat = lyr.GetNextFeature()
while feat:
# Extract ID-Info from SHP-file and other informations
    polID = feat.GetField("UniqueID")
    print("Processing Tile " + str(polID))
    # Now get the geometry, calculate corners, and build ee-feature
    geom = feat.GetGeometryRef()
    # Reproject the geometry to WGS84 --> EPSG:4326
    geom.Transform(coordTrans)
    env = geom.GetEnvelope() # Get Envelope returns a tuple (minX, maxX, minY, maxY)
    UL = [env[0], env[3]]# UR = [env[1], env[3]]
    LR = [env[1], env[2]]# LL = [env[0], env[2]]
    # Build an earth engine feature
    poly = ee.Geometry.Rectangle(coords = [UL, LR])#, LR, LL])

    #poly = ee.Feature(ee.Geometry.Rectangle(coords = [UL, LR]), {'Polygon-ID': str(polID)})

    polList.append(poly)
    feat = lyr.GetNextFeature()

#pols = ee.FeatureCollection(ee.List(polList))


# Get the Hansen layers
gfc = ee.Image(r'UMD/hansen/global_forest_change_2016_v1_4')
forest2000 = gfc.select(['treecover2000']).divide(100)
lossImage = gfc.select(['loss'])
lossYear = gfc.select(['lossyear'])
gainImage = gfc.select(['gain'])
# EE presets
reducer = ee.Reducer.sum()
maxPX = 1e13
scale = 30

tc2000_sum = forest2000.reduceRegion(ee.Reducer.mean(), poly, scale, maxPixels=maxPX).getInfo()
#tc2000_sum = forest2000.reduceRegions(pols, ee.Reducer.sum())
print(tc2000_sum)



exit(0)


