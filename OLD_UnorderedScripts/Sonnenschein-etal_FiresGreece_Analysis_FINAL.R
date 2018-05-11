#########################################################################################
#### LOAD REQUIRED LIBRARIES ####
library(reshape2) # For writing matrices as output
library(leaps) # for Best-Subsets Regression
library(hier.part) # For hierarchical partitioning
library(BMA) # For Bayesian Model Averaging
library(grDevices) # To plot the BMA-output

###############################################################
#### BUILD FUNCTIONS FOR THE REPETITIVE TYPES OF ANALYSIS #####
linearity_graph = function(data_table, variable){
  # Calculation
  sub = subset(data_table, select = c(variable,1))
  y_Name = colnames(sub[2])
  x_Name = colnames(sub[1])
  mod = lm(sub[,2]~sub[,1])
  slope = paste(c("Slope: ", round(summary(mod)$coefficients[2,1], digits = 3)), collapse="")
  intercept = paste(c("Intercept: ", round(summary(mod)$coefficients[1,1], digits = 3)), collapse="")
  R2 = paste(c("R2: ", round(summary(mod)$r.squared, digits = 3)), collapse="")
  # Graph
  outfile = paste(c(file.path(outpath,type, folder)), "/", x_Name, ".png",sep="")
  png(outfile, width=6000,height=2000,res=300)
  par(mfcol=c(1,3))
  plot(sub, main = x_Name, cex=1, cex.main=1.8, cex.axis=2, cex.lab=1.5, pch=20)
  abline(mod)
  mtext(slope, line = -2)
  mtext(intercept, line = -4)
  mtext(R2, line = -6)
  plot(residuals(mod) ~ fitted(mod), main="Residual vs. fitted values", xlab="Fitted values", ylab="Residuals", cex=1, cex.main=1.8, cex.axis=2, cex.lab=1.5, pch=20)
  qqnorm(residuals(mod), main="QQ-Plot to assess normality of residulas", cex=1, cex.main=1.8, cex.axis=2, cex.lab=1.5, pch=20)
  qqline(residuals(mod))
  dev.off()
}
linearity_table = function(data_table, nvar){
  matrix = matrix(nrow = nvar-1,ncol = 2)
  for (i in 2:nvar){
    sub = subset(data_table, select = c(i,1))
    mod = lm(sub[,2]~sub[,1])
    matrix[i-1,2] = round(summary(mod)$r.squared, digits = 3)
    matrix[i-1,1] = colnames(sub[1])
  }
  tab = as.data.frame(matrix)
  names(tab) = c("Variable", "R2")
  out_file = paste(c(file.path(outpath,type)), "/", out_table, sep="")
  write.csv(tab, file = out_file)
  }
collinearityCheck = function(IndVars_table){
     IndVars_table = independent_variables
     outputarray = array(dim=c(ncol(IndVars_table),ncol(IndVars_table)))
     dimnames(outputarray) = list(colnames(IndVars_table),colnames(IndVars_table))
     combinat = combinations(ncol(IndVars_table), 2, repeats.allowed = FALSE)
     for (c in 1:(length(combinat)/2)){
          combo = combinat[c,]
          sub = subset(IndVars_table, select = c(combo[1],combo[2]))
          y_Name = colnames(sub[2])
          x_Name = colnames(sub[1])
          title = paste(c(x_Name, " vs ", y_Name), collapse="")
          outfile = paste(c(file.path(outpath,type, folder),"/",x_Name, "_vs_", y_Name, ".png"), collapse="")
          mod_summary = summary(lm(sub))
          R2 = round(mod_summary$r.squared, digits=3)
          R2_text = paste("R2 = ", round(mod_summary$r.squared, digits=3), collapse="")
          outputarray[combo[2],combo[1]] = R2
          png(outfile, width=2000,height=2000,res=300)
          plot(sub, main = title, cex=1, cex.main=1.3, cex.axis=2, cex.lab=1.5, pch=20)
          mtext(R2_text, line = -2)
          dev.off()
     }
     tab = as.data.frame(outputarray)
     out_file = paste(c(file.path(outpath,type)), "/", out_table, sep="")
     write.csv(tab, file = out_file)
}
bestSubset = function(y_vector, x_matrix){
     bestSubsets = summary(regsubsets(x = x_matrix, y = y_vector, nvmax = 12, nbest = 25, intercept = TRUE, really.big = T, all.best = T, matrix = T, method = "exhaustive"))
     Subsets = bestSubsets$which
     AdjR2nonCV = bestSubsets$adjr2
     bestSubsets_output = as.data.frame(cbind(Subsets, AdjR2nonCV))
}
randomSubsetOfRows = function(inputTab, proportion){ #proportion for example 0.5
     inputTab[sample(nrow(inputTab), (nrow(inputTab)*proportion), replace = TRUE), ]
     
}
hierPart = function(y, x_matrix){
     HierPart = hier.part(y, x_matrix, family = "gaussian", barplot = F)
     HierPart$I.perc
}
BMA_model = function(x_matrix, y, nr_models, maxVariables, output_folder){
     # Model
     model = bicreg(x_matrix, y, nbest = nr_models, maxCol = maxVariables+1)
     # Plot01
     plot01name = paste(c(file.path(outpath,type,output_folder)), "/", type, "_ModelSelectionPlot.png", sep="")
     png(plot01name, width=5000,height=4000,res=300)
     par(oma=c(0,15,0,0))
     imageplot.bma(model, cex.axis=1.2, cex.lab=1.5, cex.main=1.3)
     text = c("Response-Variable: FIRES_FREQ")
     text = paste(c("Response-Variable: ", type), collapse="")
     mtext(text, at = -0.16, line = 1.5, font = 2, cex = 1.3)
     dev.off()
     # Plot02
     plot02name = paste(c(file.path(outpath,type,output_folder)), "/", type, "_PosteriorProbabilities.png", sep="")
     png(plot02name, width=6000,height=6000,res=300)
     par(oma=c(0,0,4,0))
     plot(model, mfrow = c(6,6), cex = 0.8)
     mtext("Posterior probabilities of variables in models", line = 6, font = 2, cex = 1.3)
     dev.off()
}
BMA_table = function(BMAmodel){
     var_coeff_mean = BMAmodel$postmean
     var_coeff_sd = BMAmodel$postsd
     prob_non0 = c("100", BMAmodel$probne0)
     cond_var_coeff_mean = BMAmodel$condpostmean
     cond_var_coeff_sd = BMAmodel$condpostsd
     cum_post_prob = c("Cum_Post_Prob_Top5", sum(BMAmodel$postprob[1:5]))
     cbind(var_coeff_mean, var_coeff_sd, prob_non0, cond_var_coeff_mean, cond_var_coeff_sd, cum_post_prob) # Compile Table
}

##############################################################
#### LOAD TABLE, SET DEPENDENT VARIABLE AND SET WORKSPACE ####
table = read.table(file.choose(), header = T)
type = "FIRES_FREQ"
outpath = "E:/kirkdata/mbaumann/Sonnenschein-etal_Fires-Greece_New-Analysis"
dir.create(file.path(outpath,type), showWarnings = FALSE)

############################
#### TEST FOR LINEARITY ####
# Establish Pre-Conditions
folder = "01_Linearity_Control_Graphs"
out_table = "01_Linearity_R2.csv"
dir.create(file.path(outpath,type, folder), showWarnings = FALSE)
n = ncol(table)
# Execute the functions
for (i in 2:n) {linearity_graph(table, i)}
linearity_table(table,n)

####################################################
#### CHECK FOR COLLINEARITIES BETWEEN VARIABLES ####
# Establish Pre-Conditions
folder = "02_Collinearity_Check"
out_table = "02_Collinearity_Check.csv"
dir.create(file.path(outpath,type, folder), showWarnings = FALSE)
# Exclude dependent variable and execute function
independent_variables = table[,-1]
collinearityCheck(independent_variables)


################################################################################################################
######################### UPDATE VARIABLES IN TABLE AND CREATE NEW INPUT FILE MANUALLY #########################
################################################################################################################
table = read.table(file.choose(), header = T)

#################################
#### BEST SUBSETS REGRESSION ####
# Format data
response = table[,1]
explanatory = table[,2:ncol(table)]
# Execute function
BS_output = bestSubset(response, explanatory)

######################################################################
#### HIERARCHICAL PARTITIONING INCLUDING n-TIMES SUBSET-MODELRUNS ####
out_table_mean = "03_BestSubset-HierPart_MultiRun_mean.csv"
out_table_std = "03_BestSubset-HierPart_MultiRun_std.csv"
nr_runs = 1000
# Establish output-tables
outputarray_mean = array(dim=c(nrow(BS_output),ncol(BS_output)))
dimnames(outputarray_mean) = list(colnames(outputarray_mean),c(colnames(BS_output)[2:(ncol(BS_output))],"R2_mean"))
outputarray_std = array(dim=c(nrow(BS_output),(ncol(BS_output)-1)))
dimnames(outputarray_std) = list(colnames(outputarray_std),c(colnames(BS_output)[2:(ncol(BS_output)-1)],"R2_std"))
# Loop through the combinations, build tmp-table of subsets
for (i in 1:nrow(BS_output)){
#for (i in 100:101){
     # Build the tmp table according to the variables    
     varNames = colnames(BS_output)[which(BS_output[i,] == 1)][-1]
     if (length(varNames) > 1){
     length(varNames)
     adjR2_nonCV = BS_output[i,"AdjR2nonCV"]
     tab_sub = cbind(response,explanatory[,varNames])
     # Make the Subset-Runs
     rsq = array(dim=c(nr_runs))
     contribs = array(dim=c(nr_runs,length(varNames)))
     for (j in 1:nr_runs){
          subb = randomSubsetOfRows(tab_sub, 0.5)
          # Do Hierarchical Partitioning
          contrib = hierPart(subb[,1], subb[,-1])
          for (k in 1:length(varNames)){
               contribs[j,k] = contrib[k,]
          }
          # Do Linear Regression
          mod = lm(subb[,1]~.,subb[,-1])
          rsq[j] = summary(mod)$adj.r.squared
          }
     
     # Write everything in the output --> R2-values
     outputarray_mean[i,"AdjR2nonCV"] = adjR2_nonCV
     outputarray_mean[i,"R2_mean"] = mean(rsq)
     outputarray_std[i,"R2_std"] = sd(rsq)
     # write everything in the output --> std-values
     for (k in 1:length(varNames)){
          outputarray_mean[i,varNames[k]] = mean(contribs[,k])
          outputarray_std[i,varNames[k]] = sd(contribs[,k])
     }
     }
}
# Write Output-Tables
out_file_mean = paste(c(file.path(outpath,type)), "/", out_table_mean, sep="")
write.csv(outputarray_mean, file = out_file_mean)
out_file_std = paste(c(file.path(outpath,type)), "/", out_table_std, sep="")
write.csv(outputarray_std, file = out_file_std)

##################################
#### BAYESIAN MODEL AVERAGING ####
# Do Pre-Work
out_table = "04_Bayesian-Model-Averaging.csv"
folder = "04_Bayesian-Model-Averaging"
dir.create(file.path(outpath,type, folder), showWarnings = FALSE)
# Execute the functions
model = BMA_model(explanatory, response, 25, ncol(explanatory), folder)
bma_table = BMA_table(model)
out_file = paste(c(file.path(outpath,type)), "/", out_table, sep="")
write.csv(bma_table, file = out_file)
# Call summary(model) to copy+paste the remaining information
summary(model)
################################################################################################################
##################################################### END ######################################################
################################################################################################################