#!/bin/bash
#run in folder where the mosaics are, and make sure the naming scheme is right
listofmosaics=`ls mosaic*.hdf`

for i in $listofmosaics
do
cat > param.txt << EOF
INPUT_FILENAME = $i

OUTPUT_FILENAME = "$i.tif"

SPECTRAL_SUBSET = ( 1 1 )

SPATIAL_SUBSET_TYPE = INPUT_LAT_LONG

SPATIAL_SUBSET_UL_CORNER = ( 49.999999996 -171.129620923 )
SPATIAL_SUBSET_LR_CORNER = ( 19.999999998 -53.208888618 )

RESAMPLING_TYPE = NEAREST_NEIGHBOR

OUTPUT_PROJECTION_TYPE = GEO

OUTPUT_PROJECTION_PARAMETERS = ( 
 0.0 0.0 0.0
 0.0 0.0 0.0
 0.0 0.0 0.0
 0.0 0.0 0.0
 0.0 0.0 0.0 )

DATUM = NoDatum

EOF

/data/gorzo/MRT/bin/resample -p param.txt
done

