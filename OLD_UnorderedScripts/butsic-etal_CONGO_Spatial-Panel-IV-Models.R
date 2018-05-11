####################################################################
#### LOAD THE PACKAGES REQUIRED FOR THE ANALYSIS ####
library(splm)
library(spdep)
library(foreign)
####################################################################
#### IMPORT THE THREE TABLES ####
data_table = read.table(file.choose(), header = T)
wdist_raw = read.table(file.choose(), header = T)
wedge_raw = read.table(file.choose(), header = T)
####################################################################
##### CREATE SPATIAL WEIGHTS OBJECTS ####
# FOR WEDGE
from_IDs = sort(unique(wedge_raw$OBJECTID))
to_IDs = sort(unique(wedge_raw$NID))
all.equal(from_IDs, to_IDs) # find the IDs used
o = order(wedge_raw$OBJECTID, wedge_raw$NID) # order the object
xx = wedge_raw[o,]
sn = data.frame(from=match(xx$OBJECTID, from_IDs), to=match(xx$NID,to_IDs), weights=xx$WEIGHT) # convert manually to a spatial.neighbours representation
attr(sn, "n") = length(from_IDs)
attr(sn, "region.id") = as.character(from_IDs)
class(sn) = c("spatial.neighbour", class(sn))
SWO_wedge = sn2listw(sn)

# FOR WDIST
from_IDs = sort(unique(wdist_raw$OBJECTID))
to_IDs = sort(unique(wdist_raw$NID))
all.equal(from_IDs, to_IDs) # find the IDs used
o = order(wdist_raw$OBJECTID, wdist_raw$NID) # order the object
xx = wdist_raw[o,]
sn = data.frame(from=match(xx$OBJECTID, from_IDs), to=match(xx$NID,to_IDs), weights=xx$WEIGHT) # convert manually to a spatial.neighbours representation
attr(sn, "n") = length(from_IDs)
attr(sn, "region.id") = as.character(from_IDs)
class(sn) = c("spatial.neighbour", class(sn))
SWO_wdist = sn2listw(sn)
###################################################################
#### EDIT THE TABLE -> ADD IDs, FORMAT FIELDS ETC. ####
data_table = subset(data_table, id != 571)
data_table = subset(data_table, id != 555)
data_table$unique_ID = c(1:length(data_table$id))
data_table$sector_ID = c(c(1:559), c(1:559),c(1:559))
#### RUN THE MODEL ####
mod_random = spgm(pdeforestm ~ paa + mindex + agindex + timbera + smarta + explorea + exploita + geoa + quarrya + dima +
           lnroada + lnpopa + watera + irria + capdist + p1 + p2 + p3 + p4 + p5 + p6 + p7 + p8 + p9, 
           data = data_table,
           index = c("sector_ID", "year"),
           listw = SWO_wdist,
           model = "random",
           lag = TRUE,
           spatial.error = TRUE,
           moments = "initial", 
           endog = "lnnoevents",
           instruments = c("neth", "cdum", "prevar"),
           verbose = FALSE,
           method = c("g2sls"),
           control = list()
           )
summary(mod_random)

roada + roada2
lnroada
