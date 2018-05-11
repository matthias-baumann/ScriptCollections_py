#### LOAD LIBRARIES NEEDED
library(xlsx)
#### LOAD TABLE
intab = read.xlsx(
  "D:/Matthias/Projects-and-Publications/Publications/Publications-in-preparation/baumann-etal_Chaco-LCLUC_Carbon/baumann-etal_LUC-Carbon-Chaco_AccuracyAssessment_02.xlsx", 1)
#### FUNCTION
reclassFunc = function(table, comboList, Truth_col, Class_col){
# add columns
  eval(parse(text=paste(c("table$Truth_reclass = table$", as.character(Truth_col)), collapse="")))
  eval(parse(text=paste(c("table$Class_reclass = table$", as.character(Class_col)), collapse="")))
# Loop through the comboList Items
  for (i in 1:length(comboList)){
    combo = comboList[i]
    toVal = combo[[1]][[2]]
    fromVals = combo[[1]][[1]]
    for (ii in 1:length(fromVals)){
      fV = fromVals[ii]
      # For Reclassification of truth-values
      eval(parse(text=paste(c("table$Truth_reclass = ifelse(table$",as.character(Truth_col),
      " == ",as.character(fV),", ", as.character(toVal),", table$Truth_reclass)"), collapse="")))
      # For Reclassification of class-values
      eval(parse(text=paste(c("table$Class_reclass = ifelse(table$",as.character(Class_col),
      " == ",as.character(fV),", ", as.character(toVal),", table$Class_reclass)"), collapse="")))
    }}
    outTab = table[,c("Class_reclass", "Truth_reclass")]
    colnames(outTab) = c("Classification", "Reference")
    return(outTab)
}

#### CLASS MERGERS
mergeList = list(
            list(c(1,17),1),
            list(c(2,3,6,7,8,9,15,16,18,19,22,23),0)
            )
#### DO THE RECLASS
tab_reclass = reclassFunc(intab, mergeList, "Truth", "ClassRun12")

table(tab_reclass)

####################### FOR PERIODWISE ANALYSIS
# (1) DEFINE MERGING CLASSES
merge8500 = list(
  list(c(1,12,13,17),1),
  list(c(5,21),2),
  list(c(4),3),
  list(c(2,3,6,7,8,9,15,16,18,19,22,23),4),
  list(c(11,14),5),
  list(c(10),6),
  list(c(20),7))

merge0013 = list(
  list(c(1,17),1),
  list(c(5,11),2),
  list(c(4,10,20),3),
  list(c(2,3,6,7,8,9,15,16,18,19,22,23),4),
  list(c(13),5),
  list(c(12),6),
  list(c(14,21),7))


# (2) SUBSET THE DATA BY ECOREGION AND THEN GET THE ERROR MATRIX
# (2-1) VER DRY CHACO
verydry_sub = subset(intab, EcoRegion == "Very Dry Chaco")
table(reclassFunc(verydry_sub, merge8500, "Truth", "ClassRun12"))
table(reclassFunc(verydry_sub, merge0013, "Truth", "ClassRun12"))
# (2-2) DRY CHACO
dry_sub = subset(intab, EcoRegion == "Dry Chaco")
table(reclassFunc(dry_sub, merge8500, "Truth", "ClassRun12"))
table(reclassFunc(dry_sub, merge0013, "Truth", "ClassRun12"))

# (2-3) HUMID CHACO
wet_sub = subset(intab, EcoRegion == "Humid Chaco")
table(reclassFunc(wet_sub, merge8500, "Truth", "ClassRun12"))
table(reclassFunc(wet_sub, merge0013, "Truth", "ClassRun12"))
