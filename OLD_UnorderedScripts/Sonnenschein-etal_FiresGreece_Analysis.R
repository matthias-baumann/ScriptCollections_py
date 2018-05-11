#########################################################################################
#### SCRIPT FOR BEST SUBSET REGRESSION INCLUDING TEST FOR LINEARITY AND COLLINEARITY ####

#### LOAD TABLE AND SET WORKSPACE ####
table = read.table(file.choose(), header = T)
str(table)

### CREATE SUBSET BY EXCLUDING ALL COUNTIES WITH RANGELAND < 1.5 ####
#table = subset(table, SN_AREA_KM2 > 1.5)

#### TEST FOR LINEARITY WITH REPSONSE VARIABLE AND PRODUCE OUTPUT-GRAPHS ####
setwd("e:/tempdata/mbaumann/2011_Sonnenschein-etal_Fires-Greece/02_Final-analysis/FIRES_PERC/Linearity_Graphs")
n = ncol(table)
for (i in 2:n) {

sub = subset(table, select = c(i,1))
y_Name = colnames(sub[2])
x_Name = colnames(sub[1])
outfile = c(x_Name, ".png")
outfile = paste(outfile, collapse="")

sub_mod = subset(table, select = c(1,i))
#sub_mod[2] = log(sub_mod[2])
#sub_mod = lapply(sub_mod, function(x){replace(x, x == -Inf, NA)})
#sub_mod = as.data.frame(sub_mod)
#library(fts)
#sub_mod = remove.na.rows(sub_mod)				# remove.na.rows removes rows which contain at least 1 NA remove.all.na rows removes rows which are all NA's
									# requires library(fts)
mod = lm(sub_mod)
mod_summary = summary(mod)
slope = mod_summary$coefficients[2,1]
slope = round(slope, digits = 3)
slope = as.character(slope)
slope = c("Slope: ", slope)
slope = paste(slope, collapse="")
intercept = mod_summary$coefficients[1,1]
intercept = round(intercept, digits = 3)
intercept = as.character(intercept)
intercept = c("Intercept: ", intercept)
intercept = paste(intercept, collapse="")
R2 = mod_summary$r.squared
R2 = round(R2, digits = 4)
R2 = as.character(R2)
R2 = c("R2 = ", R2)
R2 = paste(R2, collapse="") 

png(outfile, width=6000,height=2000,res=300)
par(mfcol=c(1,3))
plot(sub, main = outfile, cex=1, cex.main=1.8, cex.axis=2, cex.lab=1.5, pch=20)
abline(mod)
mtext(slope, line = -2)
mtext(intercept, line = -4)
mtext(R2, line = -6)
plot(residuals(mod) ~ fitted(mod), main="Residual vs. fitted values", xlab="Fitted values", ylab="Residuals", cex=1, cex.main=1.8, cex.axis=2, cex.lab=1.5, pch=20)
qqnorm(residuals(mod), main="QQ-Plot to assess normality of residulas", cex=1, cex.main=1.8, cex.axis=2, cex.lab=1.5, pch=20)
qqline(residuals(mod))
dev.off()
}


#### CHECK FOR COLLINEARITIES BETWEEN VARIABLES ####
outputarray = array(dim=c(n-1,n-1))
var_names = colnames(table)
var_names = var_names[-1]
dimnames(outputarray) = list(var_names, var_names)

setwd("e:/tempdata/mbaumann/2011_Sonnenschein-etal_Fires-Greece/02_Final-analysis/FIRES_PERC/Collinearity_Graphs")
for (i in 2:(n-1)) {
for (j in (i+1):n) {

sub = subset(table, select = c(i,j))

y_Name = colnames(sub[2])
x_Name = colnames(sub[1])
title = c(x_Name, " vs. ", y_Name)
title = paste(title, collapse="")
outfile = c(x_Name, "_vs_", y_Name, ".png")
outfile = paste(outfile, collapse="")

mod = lm(sub)
mod_summary = summary(mod)
R2 = mod_summary$r.squared
R2 = round(R2, digits = 3)
R2char = as.character(R2)
R2char = c("R2 = ", R2)
R2char = paste(R2char, collapse="")

x = i-1
y = j-1
outputarray[x,y] = R2

png(outfile, width=2000,height=2000,res=300)
plot(sub, main = title, cex=1, cex.main=1.3, cex.axis=2, cex.lab=1.5, pch=20)
mtext(R2char, line = -2)
dev.off()
}
}
write.table(outputarray, file = "CollinearityTest.txt", sep = ",")

######################################################################
#### UPDATE VARIABLES IN TABLE AND CREATE NEW INPUT FILE MANUALLY ####
######################################################################

#### APPLY BEST SUBSETS ####
table = read.table(file.choose(), header = T)
str(table)


setwd("D:/Matthias/Publications/Publications-in-preparation/2011_Sonnenschein-etal_Fires-Greece/02_Final-analysis/FIRES_FREQ/BestSubset_HierPart")
n = ncol(table)

library(leaps)
response = table[,1]
explanatory = table[,2:n]

bestSubsets = summary(regsubsets(x = explanatory, y = response, nvmax = 12, nbest = 25, intercept = TRUE, really.big = T, all.best = T, matrix = T, method = "exhaustive"))
Subsets = bestSubsets$which
SubsetsAdjR2 = bestSubsets$adjr2
SubsetsBIC = bestSubsets$bic
SubsetsRSS = bestSubsets$rss
SubsetsR2 = bestSubsets$rsq
SubsetsOUTMAT = bestSubsets$outmat
outputTableArray = cbind(Subsets, SubsetsR2, SubsetsAdjR2, SubsetsBIC, SubsetsRSS)
write.table(outputTableArray, file = "BestSubset_Output.txt", sep = ",")

#### DO HIERARCHICAL PARTITIONING ####
library(hier.part)
VarBS_Table = outputTableArray
tab_tmp = VarBS_Table
row = nrow(VarBS_Table)
header = tab_tmp[-(2:row),]
header = t(header)
outfile = header

startrow = ncol(table) + 1
for (i in startrow:row){									# Start-Row is str(table) above +1
rowSubset = VarBS_Table[i, ]
rowSubset = lapply(rowSubset, function(x){replace(x, x == 0, NA)})	# convert 0/FALSE into NA
R2 = rowSubset$SubsetsR2
adjR2 = rowSubset$SubsetsAdjR2
BIC = rowSubset$SubsetsBIC
RSS = rowSubset$SubsetsRSS
tmpTable = merge(explanatory, rowSubset, all.y = TRUE, all.x = TRUE)	# merge the subset line with the explanatory variables
rows = nrow(tmpTable)
tmpTable = tmpTable[,complete.cases(t(tmpTable))]		# remove all columns that have at least one NA
tmpTable = tmpTable[-rows,]					# remove the last row, where the 0/1 were stored
HierPart = hier.part(response, tmpTable, family = "gaussian", barplot = F)
out_tmp = as.data.frame(HierPart$I.perc)
out_tmp = t(out_tmp)
tab_tmp = merge(header, out_tmp, all.y = TRUE, all.x = TRUE)
tab_tmp = tab_tmp[2, ]
cols = ncol(tab_tmp)
tab_tmp$SubsetsR2 = R2
tab_tmp$SubsetsAdjR2 = adjR2
tab_tmp$SubsetsBIC = BIC
tab_tmp$SubsetsRSS = RSS
outfile = rbind(outfile, tab_tmp)
}
write.table(outfile, file = "HierPart_Output.txt", sep = ",")


#### DO BAYESIAN MODEL AVERAGING ####
library(BMA)
library(grDevices)
table = read.table(file.choose(), header = T)
setwd("E:/tempdata/mbaumann/2011_Sonnenschein-etal_Fires-Greece/02_Final-analysis/FIRES_FREQ/BMA")

y_variable = table[,1]								# Create the response variable
x_variables = table[,2:ncol(table)]						# Create matrix with explanatory variables


model = bicreg(x_variables, y_variable, nbest = 25, maxCol = 36)# variables + 1 to consider intercept

var_names = c("Intercept", model$namesx)					# Variables in the model --> add "Intercept to get the correct numbers of rows
var_coeff_mean = model$postmean						# the posterior mean of each coefficient (from model averaging)
var_coeff_sd = model$postsd							# the posterior standard deviation of each coefficient (from model averaging)
prob_non0 = c("100", model$probne0)							# Posterior probability that variables are not zero
cond_var_coeff_mean = model$condpostmean					# the posterior mean of each coefficient conditional on the variable being included in the model
cond_var_coeff_sd = model$condpostsd					# the posterior standard deviation of each coefficient conditional on the variable being included in the model

cum_post_prob = c("Cum_Post_Prob_Top5", sum(model$postprob[1:5]))	# Cummulative posterior probability of the best 5 models --> R usually gives that as a measure
length(cum_post_prob) = length(var_names)					# So that we have NAs in the remaining rows

output_BMA = cbind(var_names, var_coeff_mean, var_coeff_sd, prob_non0, cond_var_coeff_mean, cond_var_coeff_sd, cum_post_prob) # Compile Table
tablename = c("FIRES_FREQ_BMA-output.txt")
tablename = paste(tablename, collapse="")
write.table(output_BMA, file = tablename, sep = ",")			# Write output table

plot01name = c("FIRES_FREQ_", "ModelSelectionPlot.png")
plot01name = paste(plot01name, collapse="")
png(plot01name, width=5000,height=4000,res=300)
par(oma=c(0,15,0,0))
imageplot.bma(model, cex.axis=1.2, cex.lab=1.5, cex.main=1.3)
text = c("Response-Variable: FIRES_FREQ")
text = paste(text, collapse="")
mtext(text, at = -0.16, line = 1.5, font = 2, cex = 1.3)
dev.off()

plot02name = c("FIRES_FREQ_", "PosteriorProbabilities.png")
plot02name = paste(plot02name, collapse="")
png(plot02name, width=6000,height=6000,res=300)
par(oma=c(0,0,4,0))
plot(model, mfrow = c(6,6), cex = 0.8)
mtext("Posterior probabilities of variables in models", line = 6, font = 2, cex = 1.3)
dev.off()

