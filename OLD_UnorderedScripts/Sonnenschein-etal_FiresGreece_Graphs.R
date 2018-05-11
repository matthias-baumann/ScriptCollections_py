########################################
#### IMPORT EDITED TABLE FROM EXCEL ####
########################################

library(grDevices)

table = read.table(file.choose(), header = T)
str(table)
setwd("D:/Matthias/Publications/Publications-in-preparation/2012_Sonnenschein-etal_Fires-Greece/02_Final-analysis/FIRES_FREQ/BestSubset_HierPart_ordered")
n = ncol(table)
names = dimnames(table)
groupnames = c(rep("Rangeland Management", 11),rep("Rangeland Conditions and development", 11), rep("Topography", 4), rep("Climate", 5), rep("Demography", 2), rep("Remoteness", 2), rep("Accessibility", 1))
groupcolors = c(rep("burlywood", 11), rep("coral", 11), rep("cadetblue3", 4), rep("cornsilk2", 5), rep("aquamarine3", 2), rep("chartreuse3", 2), rep("darkgoldenrod3", 1))

var_num = c(2:12)
for (i in var_num){

av_table = subset(table, Variables_in_Model == i)					#
R2 = av_table$R2
AdjR2 = av_table$AdjR2
av_table = av_table[,2:(n-2)]
average = lapply(av_table, mean, na.rm = TRUE)
average = t(average)
mask = apply(average, 2, is.na)
average[mask] = 0
count = lapply(av_table, function(x){length(which(x>0))})
count = t(count)

title = c("Number of variables in model: ", i)						#
title = paste(title, collapse="")
file_name = c(i, "_variables.png") 
file_name = paste(file_name, collapse="")
r2max = c("Max. R2 = ", round(max(R2), digits = 3))
r2max = paste(r2max, collapse="")
r2min = c("Min. R2 = ", round(min(R2), digits = 3))
r2min = paste(r2min, collapse="")
r2mean = c("Mean R2 = ", round(mean(R2), digits = 3))
r2mean = paste(r2mean, collapse="")
Adjr2max = c("Max. Adj. R2 = ", round(max(AdjR2), digits = 3))
Adjr2max = paste(Adjr2max, collapse="")
Adjr2min = c("Min. Adj. R2 = ", round(min(AdjR2), digits = 3))
Adjr2min = paste(Adjr2min, collapse="")
Adjr2mean = c("Mean Adj. R2 = ", round(mean(AdjR2), digits = 3))
Adjr2mean = paste(Adjr2mean, collapse="")

# Start png device and build matrix
png(file_name, width=7, height=10,units = "in", res=300)

#par(mfcol=c(1,2))
layout(matrix(c(1,1,1,1,1,1,2,2,2,2),1,10,byrow = TRUE))
layout.show(2)

# Plot 1 + first part of text boxes
par(mar=c(5,17,7,0))
barplot(average, horiz = TRUE, xlim = rev(c(0,100)), las=1, width = 4, axes = TRUE, cex.axis = 1.4, xlab = "% Variance explained \n Hierarchical Partitioning")
axis(side = 3, labels = TRUE, cex.axis = 1.4, hadj = 0.15)
mtext(Adjr2mean, at = 170, line = 5, cex = 0.8)
mtext(Adjr2max, at = 169, line = 3.5, cex = 0.8)
mtext(Adjr2min, at = 168.5, line = 2, cex = 0.8)

# Plot 2 + second part of text boxes
par(mar=c(5,0,7,6))
labelOff = ncol(count)
names = rep("",labelOff)
barplot(count, horiz = TRUE, width = 4, names.arg = names, las=3, axes = TRUE, las=1, cex.axis = 1.4, xlim = c(0,26), offset = 0.5, xlab = "Number Models entered \n Best Subset Regression")
axis(side = 3, labels = TRUE, hadj = 0.2, cex.axis = 1.4)
mtext(title, at = 0.5, line = 3.5, font = 2, cex = 1.6)

dev.off()
}
