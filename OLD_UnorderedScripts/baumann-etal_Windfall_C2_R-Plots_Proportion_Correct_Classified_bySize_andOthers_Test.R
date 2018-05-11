################################################################################################################################################
#### LOAD THE REQUIRED PACKAGES ####
library(ggplot2)
library(grDevices)
library(gridExtra)
library(RGraphics)
################################################################################################################################################
#### DO THE ANALYSIS (DISTURBANCE-TYPE INDEX), AND CREATE  ####
RAW_table = read.table(file.choose(), header = T)
table = subset(RAW_table, Area_m2 > 5400)

table$table_Diff = table$R_B5_11_ST + table$TC_B_11_ST - table$TC_W_11_ST
table$Class = 0
table$Class[which(table$table_Diff < 0)] = 1
##################################################################################################################################################
#### BUILD THE PLOTS ####
# CREATE SUBSET TABLE WITH ONLY THE STUFF WE WANT
plot_table = subset(table, , c(THICKNESS, Wind01_New, Class))
# GET THE LEVELS FROM THE AREA_VARIABLE
pol_sizes = levels(as.factor(plot_table$THICKNESS))
n = length(pol_sizes)
# CREATE OUTPUT-LISTS
sizes = numeric()
prop_all = numeric()
numPol_all = numeric()
prop_wind = numeric()
numPol_wind = numeric()
prop_other = numeric()
numPol_other = numeric()
# NOW LOOP THROUGH THE LEVELS AND GET THE PROPORTION CORRECTLY CLASSIFIED
for (i in 1:n){
  size = pol_sizes[i]
  tmp_all = subset(plot_table, THICKNESS == as.numeric(size))
  tmp_wind = subset(plot_table, THICKNESS == as.numeric(size) & Wind01_New == 1)
  tmp_other = subset(plot_table, THICKNESS == as.numeric(size) & Wind01_New == 0)
  # Calculate the proportions --> ALL
  tmp_all$eval = ifelse(tmp_all$Wind01_New == tmp_all$Class,1,0)
  p_all = sum(tmp_all$eval) / length(tmp_all$Class)
  # --> Windfall
  tmp_wind$eval = ifelse(tmp_wind$Wind01_New == tmp_wind$Class,1,0)
  p_wind = sum(tmp_wind$eval) / length(tmp_wind$Class)
  # --> Other
  tmp_other$eval = ifelse(tmp_other$Wind01_New == tmp_other$Class,1,0)
  p_other = sum(tmp_other$eval) / length(tmp_other$Class)   
  # Write into output-array
  sizes = c(sizes,as.numeric(size))
  prop_all = c(prop_all, as.numeric(p_all))
  numPol_all = c(numPol_all, as.numeric(length(tmp_all$Class)))
  prop_wind = c(prop_wind, as.numeric(p_wind))
  numPol_wind = c(numPol_wind, as.numeric(length(tmp_wind$Class)))  
  prop_other = c(prop_other, as.numeric(p_other))
  numPol_other = c(numPol_other, as.numeric(length(tmp_other$Class))) 
}
# CONCATENATE OUTPUT-VECTORS INTO NEW TABLE AND EDIT HEADERS
out = data.frame(cbind(sizes, prop_all, numPol_all, prop_wind, numPol_wind, prop_other, numPol_other))
# Add Comparison with Pixel size as new column
out$px = out$sizes / 900
colnames(out) = c("Pol_Size_m2", "Prop_Cor_All", "Num_Pol_All", "Prop_Cor_Wind", "Num_Pol_Wind", "Prop_Cor_Other", "Num_Pol_Other", "PX")
# BUILD THE PLOT (criteria for minimum polygons in class --> 5)
crit = 1
# build plot for both classes together
out_sub = subset(out, Num_Pol_All >= crit)
plot_all <- ggplot(out_sub, aes(x = Pol_Size_m2, y = Prop_Cor_All)) +
  geom_point(size = 2) + 
  stat_smooth(method = "loess", se = TRUE, level = 0.95, geom = "smooth", size = 1) + 
  scale_x_continuous("Size of disturbance patch [ha]") + 
  scale_y_continuous("Proportion Correctly classified Polygons", limits = c(0.4,1)) +
  ggtitle("'Windfall' + 'Other'") +
  theme(plot.title = element_text(lineheight = 0.5, face = "bold", size = 20))
# build the same graph with windfall only
out_sub = subset(out, Num_Pol_Wind >= crit)
plot_wind <- ggplot(out_sub, aes(x = Pol_Size_m2, y = Prop_Cor_Wind)) +
  geom_point(size = 2) + 
  stat_smooth(method = "loess", se = TRUE, level = 0.95, geom = "smooth", size = 1) + 
  scale_x_continuous("Size of disturbance patch [ha]") + 
  scale_y_continuous("Proportion Correctly classified Polygons", limits = c(0.4,1)) +
  ggtitle("'Windfall'") +
  theme(plot.title = element_text(lineheight = 0.5, face = "bold", size = 20))
# build the same graph with 'other' only
out_sub = subset(out, Num_Pol_Other >= crit)
plot_other <- ggplot(out_sub, aes(x = Pol_Size_m2, y = Prop_Cor_Other)) +
  geom_point(size = 2) + 
  stat_smooth(method = "loess", se = TRUE, level = 0.95, geom = "smooth", size = 1) + 
  scale_x_continuous("Size of disturbance patch [ha]") + 
  scale_y_continuous("Proportion Correctly classified Polygons", limits = c(0.4,1)) +
  ggtitle("'Other'") +
  theme(plot.title = element_text(lineheight = 0.5, face = "bold", size = 20))
# plot the three graphs next to each other
png("d:/accuracy_THICKNESS.png", width=6000,height=2000,res=300)
grid.arrange(arrangeGrob(plot_all, plot_wind, plot_other, nrow = 1))
dev.off()

##################################################################################################################################################
#### DO THE SAME WITH A WEIGHTED AVERAGE VALUE OF THE TWO NEIGHBORING POLYGON SIZES ####
plot_table = subset(table, , c(THICKNESS, Wind01_New, Class))
pol_sizes = levels(as.factor(plot_table$AXIS_Ratio))
# build lists for indexes to define upper limits and lower limits
ll = seq(1,length(pol_sizes)+1,3)
# create output lists
sizes = numeric()
prop_all = numeric()
numPol_all = numeric()
prop_wind = numeric()
numPol_wind = numeric()
prop_other = numeric()
numPol_other = numeric()
# now loop though the indeces
for (i in 1:length(ll)){
  ll_size = pol_sizes[i]
  ul_size = pol_sizes[i+1]
  # subset the table
  tmp_all = subset(plot_table, THICKNESS >= as.numeric(ll_size) & THICKNESS <= as.numeric(ul_size))
  tmp_wind = subset(plot_table, THICKNESS >= as.numeric(ll_size) & THICKNESS <= as.numeric(ul_size) & Wind01_New == 1)
  tmp_other = subset(plot_table, THICKNESS >= as.numeric(ll_size) & THICKNESS <= as.numeric(ul_size) & Wind01_New == 0)
  # Calculate the proportions --> ALL
  tmp_all$eval = ifelse(tmp_all$Wind01_New == tmp_all$Class,1,0)
  p_all = sum(tmp_all$eval) / length(tmp_all$Class)
  # --> Windfall
  tmp_wind$eval = ifelse(tmp_wind$Wind01_New == tmp_wind$Class,1,0)
  p_wind = sum(tmp_wind$eval) / length(tmp_wind$Class)
  # --> Other
  tmp_other$eval = ifelse(tmp_other$Wind01_New == tmp_other$Class,1,0)
  p_other = sum(tmp_other$eval) / length(tmp_other$Class)   
  # Write into output-array
  sizes = c(sizes,as.numeric(ul_size))
  prop_all = c(prop_all, as.numeric(p_all))
  numPol_all = c(numPol_all, as.numeric(length(tmp_all$Class)))
  prop_wind = c(prop_wind, as.numeric(p_wind))
  numPol_wind = c(numPol_wind, as.numeric(length(tmp_wind$Class)))  
  prop_other = c(prop_other, as.numeric(p_other))
  numPol_other = c(numPol_other, as.numeric(length(tmp_other$Class))) 
}
# concatenate output values into dataframe
out = data.frame(cbind(sizes, prop_all, numPol_all, prop_wind, numPol_wind, prop_other, numPol_other))
# Add Comparison with Pixel size as new column, edit column names
out$px = out$sizes / 900
colnames(out) = c("Pol_Size_m2", "Prop_Cor_All", "Num_Pol_All", "Prop_Cor_Wind", "Num_Pol_Wind", "Prop_Cor_Other", "Num_Pol_Other", "PX")

# build plot for both classes together
plot_all <- ggplot(out, aes(x = Pol_Size_m2, y = Prop_Cor_All)) +
  geom_point(size = 2) + 
  stat_smooth(method = "loess", se = TRUE, level = 0.95, geom = "smooth", size = 1) + 
  scale_x_continuous("THICKNESS of disturbance patch") + 
  scale_y_continuous("Proportion Correctly classified Polygons", limits = c(0.4,1)) +
  ggtitle("'Windfall' + 'Other'") +
  theme(plot.title = element_text(lineheight = 0.5, face = "bold", size = 20))
# build the same graph with windfall only
plot_wind <- ggplot(out, aes(x = Pol_Size_m2, y = Prop_Cor_Wind)) +
  geom_point(size = 2) + 
  stat_smooth(method = "loess", se = TRUE, level = 0.95, geom = "smooth", size = 1) + 
  scale_x_continuous("THICKNESS of disturbance patch") + 
  scale_y_continuous("Proportion Correctly classified Polygons", limits = c(0.4,1)) +
  ggtitle("'Windfall'") +
  theme(plot.title = element_text(lineheight = 0.5, face = "bold", size = 20))
# build the same graph with 'other' only
plot_other <- ggplot(out, aes(x = Pol_Size_m2, y = Prop_Cor_Other)) +
  geom_point(size = 2) + 
  stat_smooth(method = "loess", se = TRUE, level = 0.95, geom = "smooth", size = 1) + 
  scale_x_continuous("THICKNESS of disturbance patch") + 
  scale_y_continuous("Proportion Correctly classified Polygons", limits = c(0.4,1)) +
  ggtitle("'Other'") +
  theme(plot.title = element_text(lineheight = 0.5, face = "bold", size = 20))
# plot the three graphs next to each other
png("d:/accuracy_AXIS_Ratio.png", width=6000,height=2000,res=300)
grid.arrange(arrangeGrob(plot_all, plot_wind, plot_other, nrow = 1))
dev.off()

##################################################################################################################################################
#### Create plots to plot variables vs. size --> all four cases ####

plot_table = subset(table, , c(Class, Wind01_New, Area_m2, TC_B_11_ST, TC_W_11_ST, R_B5_11_ST))
plot_table$ErrorMatrix = "NA"
plot_table$ErrorMatrix = ifelse(plot_table$Class == 1 & plot_table$Wind01_New == 1, "True Windfall", plot_table$ErrorMatrix)
plot_table$ErrorMatrix = ifelse(plot_table$Class == 0 & plot_table$Wind01_New == 0, "True Other", plot_table$ErrorMatrix)
plot_table$ErrorMatrix = ifelse(plot_table$Class == 1 & plot_table$Wind01_New == 0, "False Windfall", plot_table$ErrorMatrix)
plot_table$ErrorMatrix = ifelse(plot_table$Class == 0 & plot_table$Wind01_New == 1, "False Other", plot_table$ErrorMatrix)
plot_table$ErrorMatrix = as.factor(plot_table$ErrorMatrix)
#plot_table$Area_ha = plot_table$Area_m2 / 10000

# test for only false classified polygons
#plot_table = subset(plot_table, ErrorMatrix == "False Windfall" | ErrorMatrix == "False Other")

nrow(subset(plot_table, ErrorMatrix == "True Windfall"))
nrow(subset(plot_table, ErrorMatrix == "True Other"))
nrow(subset(plot_table, ErrorMatrix == "False Windfall"))
nrow(subset(plot_table, ErrorMatrix == "False Other"))

# build plot for tasselled cap brightness
plot_TCB <- ggplot(plot_table, aes(x = log(Area_ha), y = TC_B_11_ST)) + 
  geom_point(aes(colour = ErrorMatrix), size = 1.5) +
  scale_x_continuous("Size of disturbance patch log(ha)") +
  scale_y_continuous("Mean Tasseled Cap Brightness") +
  ggtitle("Patch size vs. Tasseled Cap Brightness") +
  theme(plot.title = element_text(lineheight = 0.5, face = "bold", size = 20), legend.position = c(1,1), legend.justification = c(1,1),
  legend.text = element_text(size = 16, face = "bold"), legend.title = element_blank())
# tasselled cap wetness
plot_TCW <- ggplot(plot_table, aes(x = log(Area_ha), y = TC_W_11_ST)) + 
  geom_point(aes(colour = ErrorMatrix), size = 1.5) +
  scale_x_continuous("Size of disturbance patch log(ha)") +
  scale_y_continuous("Mean Tasseled Cap Wetness") +
  ggtitle("Patch size vs. Tasseled Cap Wetness") +
  theme(plot.title = element_text(lineheight = 0.5, face = "bold", size = 20), legend.position = c(1,1), legend.justification = c(1,1),
  legend.text = element_text(size = 16, face = "bold"), legend.title = element_blank())
# R-B5
plot_RB5 <- ggplot(plot_table, aes(x = log(Area_ha), y = R_B5_11_ST)) + 
  geom_point(aes(colour = ErrorMatrix), size = 1.5) +
  scale_x_continuous("Size of disturbance patch log(ha)") +
  scale_y_continuous("Mean Band5 Reflectance") +
  ggtitle("Patch size vs. Band 5") +
  theme(plot.title = element_text(lineheight = 0.5, face = "bold", size = 20), legend.position = c(1,1), legend.justification = c(1,1),
  legend.text = element_text(size = 16, face = "bold"), legend.title = element_blank())
# plot the three graphs next to each other
png("d:/Variables_ErrorMatrix.png", width=6000,height=2000,res=300)
grid.arrange(arrangeGrob(plot_TCB, plot_TCW, plot_RB5, nrow = 1))
dev.off()

##################################################################################################################################################
#### GENERATE TABLE TO SEE FOR FALSE POLYGONS WHICH FACTOR'S FAULT IT WAS ####
table_table = subset(table, , c(Class, Wind01_New, Area_m2, TC_B_11_ST, TC_W_11_ST, R_B5_11_ST))
table_table$ErrorMatrix = "NA"
table_table$ErrorMatrix = ifelse(table_table$Class == 1 & table_table$Wind01_New == 1, "True Windfall", table_table$ErrorMatrix)
table_table$ErrorMatrix = ifelse(table_table$Class == 0 & table_table$Wind01_New == 0, "True Other", table_table$ErrorMatrix)
table_table$ErrorMatrix = ifelse(table_table$Class == 1 & table_table$Wind01_New == 0, "False Windfall", table_table$ErrorMatrix)
table_table$ErrorMatrix = ifelse(table_table$Class == 0 & table_table$Wind01_New == 1, "False Other", table_table$ErrorMatrix)

# derive information, add to vectors
cond_o = character()
cases_o = numeric()
# windfall omission
# True conditions for windfall --> RB5 < 0, TC_B < 0, TC_W > 0
wind_omission = subset(table_table, ErrorMatrix == "False Other")
C1C2C3_o = nrow(subset(wind_omission, R_B5_11_ST < 0 & TC_B_11_ST < 0 & TC_W_11_ST > 0))
cond_o = c(cond_o, "C1C2C3_o")
cases_o = c(cases_o, C1C2C3_o)
C1C2_o = nrow(subset(wind_omission, R_B5_11_ST < 0 & TC_B_11_ST < 0 & TC_W_11_ST < 0))
cond_o = c(cond_o, "C1C2_o")
cases_o = c(cases_o, C1C2_o)
C2C3_o = nrow(subset(wind_omission, R_B5_11_ST > 0 & TC_B_11_ST < 0 & TC_W_11_ST > 0))
cond_o = c(cond_o, "C2C3_o")
cases_o = c(cases_o, C2C3_o)
C1C3_o = nrow(subset(wind_omission, R_B5_11_ST < 0 & TC_B_11_ST > 0 & TC_W_11_ST > 0))
cond_o = c(cond_o, "C1C3_o")
cases_o = c(cases_o, C1C3_o)
C1_o = nrow(subset(wind_omission, R_B5_11_ST < 0 & TC_B_11_ST > 0 & TC_W_11_ST < 0))
cond_o = c(cond_o, "C1_o")
cases_o = c(cases_o, C1_o)
C2_o = nrow(subset(wind_omission, R_B5_11_ST > 0 & TC_B_11_ST < 0 & TC_W_11_ST < 0))
cond_o = c(cond_o, "C2_o")
cases_o = c(cases_o, C2_o)
C3_o = nrow(subset(wind_omission, R_B5_11_ST > 0 & TC_B_11_ST > 0 & TC_W_11_ST > 0))
cond_o = c(cond_o, "C3_o")
cases_o = c(cases_o, C3_o)
None_o = nrow(subset(wind_omission, R_B5_11_ST > 0 & TC_B_11_ST > 0 & TC_W_11_ST < 0))
cond_o = c(cond_o, "None_o")
cases_o = c(cases_o, None_o)

tab_omission = rbind(cond_o, cases_o)
tab_omission
# windfall comission
cond_c = character()
cases_c = numeric()
wind_comission = subset(table_table, ErrorMatrix == "False Windfall")
C1C2C3_c = nrow(subset(wind_comission, R_B5_11_ST > 0 & TC_B_11_ST > 0 & TC_W_11_ST < 0))
cond_c = c(cond_c, "C1C2C3_c")
cases_c = c(cases_c, C1C2C3_c)
C1C2_c = nrow(subset(wind_comission, R_B5_11_ST > 0 & TC_B_11_ST > 0 & TC_W_11_ST > 0))
cond_c = c(cond_c, "C1C2_c")
cases_c = c(cases_c, C1C2_c)
C2C3_c = nrow(subset(wind_comission, R_B5_11_ST < 0 & TC_B_11_ST > 0 & TC_W_11_ST < 0))
cond_c = c(cond_c, "C2C3_c")
cases_c = c(cases_c, C2C3_c)
C1C3_c = nrow(subset(wind_comission, R_B5_11_ST > 0 & TC_B_11_ST < 0 & TC_W_11_ST < 0))
cond_c = c(cond_c, "C1C3_c")
cases_c = c(cases_c, C1C3_c)
C1_c = nrow(subset(wind_comission, R_B5_11_ST > 0 & TC_B_11_ST < 0 & TC_W_11_ST > 0))
cond_c = c(cond_c, "C1_c")
cases_c = c(cases_c, C1_c)
C2_c = nrow(subset(wind_comission, R_B5_11_ST < 0 & TC_B_11_ST > 0 & TC_W_11_ST > 0))
cond_c = c(cond_c, "C2_c")
cases_c = c(cases_c, C2_c)
C3_c = nrow(subset(wind_comission, R_B5_11_ST < 0 & TC_B_11_ST < 0 & TC_W_11_ST < 0))
cond_c = c(cond_c, "C3_c")
cases_c = c(cases_c, C3_c)
None_c = nrow(subset(wind_comission, R_B5_11_ST < 0 & TC_B_11_ST < 0 & TC_W_11_ST > 0))
cond_c = c(cond_c, "None_c")
cases_c = c(cases_c, None_c)
tab_comission = rbind(cond_c, cases_c)
tab_comission

# windfall correct
cond_corr = character()
cases_corr = numeric()
wind_correct = subset(table_table, ErrorMatrix == "True Windfall")
C1C2C3_corr = nrow(subset(wind_correct, R_B5_11_ST <= 0 & TC_B_11_ST <= 0 & TC_W_11_ST >= 0))
cond_corr = c(cond_corr, "C1C2C3_corr")
cases_corr = c(cases_corr, C1C2C3_corr)
C1C2_corr = nrow(subset(wind_correct, R_B5_11_ST <= 0 & TC_B_11_ST <= 0 & TC_W_11_ST < 0))
cond_corr = c(cond_corr, "C1C2_corr")
cases_corr = c(cases_corr, C1C2_corr)
C2C3_corr = nrow(subset(wind_correct, R_B5_11_ST > 0 & TC_B_11_ST <= 0 & TC_W_11_ST >= 0))
cond_corr = c(cond_corr, "C2C3_corr")
cases_corr = c(cases_corr, C2C3_corr)
C1C3_corr = nrow(subset(wind_correct, R_B5_11_ST <= 0 & TC_B_11_ST > 0 & TC_W_11_ST >= 0))
cond_corr = c(cond_corr, "C1C3_corr")
cases_corr = c(cases_corr, C1C3_corr)
C1_corr = nrow(subset(wind_correct, R_B5_11_ST <= 0 & TC_B_11_ST > 0 & TC_W_11_ST < 0))
cond_corr = c(cond_corr, "C1_corr")
cases_corr = c(cases_corr, C1_corr)
C2_corr = nrow(subset(wind_correct, R_B5_11_ST > 0 & TC_B_11_ST <= 0 & TC_W_11_ST < 0))
cond_corr = c(cond_corr, "C2_corr")
cases_corr = c(cases_corr, C2_corr)
C3_corr = nrow(subset(wind_correct, R_B5_11_ST > 0 & TC_B_11_ST > 0 & TC_W_11_ST >= 0))
cond_corr = c(cond_corr, "C3_corr")
cases_corr = c(cases_corr, C3_corr)
None_corr = nrow(subset(wind_correct, R_B5_11_ST > 0 & TC_B_11_ST > 0 & TC_W_11_ST < 0))
cond_corr = c(cond_corr, "None_corr")
cases_corr = c(cases_corr, None_corr)

tab_correct = rbind(cond_corr, cases_corr)
tab_correct






























