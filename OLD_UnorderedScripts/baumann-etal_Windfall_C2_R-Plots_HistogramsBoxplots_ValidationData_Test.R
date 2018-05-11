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

table$AXIS_Ratio = table$MAJORAXIS / table$MINORAXIS
table$table_Diff = table$R_B5_11_ST + table$TC_B_11_ST - table$TC_W_11_ST
table$Class = 0
table$Class[which(table$table_Diff < 0)] = 1

##################################################################################################################################################
#### Create plots to plot variables vs. size --> all four cases ####
plot_table = subset(table, , c(Class, Wind01_New, Area_m2, TC_B_11_ST, TC_W_11_ST, R_B5_11_ST))
plot_table$ErrorMatrix = "NA"
plot_table$ErrorMatrix = ifelse(plot_table$Class == 1 & plot_table$Wind01_New == 1, "True Windfall", plot_table$ErrorMatrix)
plot_table$ErrorMatrix = ifelse(plot_table$Class == 0 & plot_table$Wind01_New == 0, "True Other", plot_table$ErrorMatrix)
plot_table$ErrorMatrix = ifelse(plot_table$Class == 1 & plot_table$Wind01_New == 0, "False Windfall", plot_table$ErrorMatrix)
plot_table$ErrorMatrix = ifelse(plot_table$Class == 0 & plot_table$Wind01_New == 1, "False Other", plot_table$ErrorMatrix)
plot_table$ErrorMatrix = as.factor(plot_table$ErrorMatrix)
plot_table$Area_ha = plot_table$Area_m2 / 10000
# Rename the labels for windfall/other
plot_table$Wind01_New = factor(plot_table$Wind01_New, labels = c("Other", "Windfall"))

# Plots for Tasseled Cap Brightness
# build plot for areas > 1ha
ha1_table = subset(plot_table, Area_ha >= 1)
plot_TCB1ha <- ggplot(ha1_table, aes(x = TC_B_11_ST, fill = as.factor(Wind01_New))) +
  geom_histogram(binwidth = 0.05, alpha = 0.5, position = "identity") + 
  scale_x_continuous("Normalized Mean Tasseled Cap Brightness") +
  theme(plot.title = element_text(lineheight = 0.5, face = "bold", size = 20), legend.position = c(1,1), legend.justification = c(1,1),
  legend.text = element_text(size = 16, face = "bold"), legend.title = element_blank()) +
  ggtitle("Areas > 1 ha")
# build plot for areas > 2ha
ha2_table = subset(plot_table, Area_ha >= 2)
plot_TCB2ha <- ggplot(ha2_table, aes(x = TC_B_11_ST, fill = as.factor(Wind01_New))) +
  geom_histogram(binwidth = 0.05, alpha = 0.5, position = "identity") + 
  scale_x_continuous("Normalized Mean Tasseled Cap Brightness") +
  theme(plot.title = element_text(lineheight = 0.5, face = "bold", size = 20), legend.position = c(1,1), legend.justification = c(1,1),
        legend.text = element_text(size = 16, face = "bold"), legend.title = element_blank()) +
  ggtitle("Areas > 2 ha")
# build plot for areas > 5ha
ha5_table = subset(plot_table, Area_ha >= 5)
plot_TCB5ha <- ggplot(ha5_table, aes(x = TC_B_11_ST, fill = as.factor(Wind01_New))) +
  geom_histogram(binwidth = 0.05, alpha = 0.5, position = "identity") + 
  scale_x_continuous("Normalized Mean Tasseled Cap Brightness") +
  theme(plot.title = element_text(lineheight = 0.5, face = "bold", size = 20), legend.position = c(1,1), legend.justification = c(1,1),
        legend.text = element_text(size = 16, face = "bold"), legend.title = element_blank()) +
  ggtitle("Areas > 5 ha")
# build plot for areas > 10ha
ha10_table = subset(plot_table, Area_ha >= 10)
plot_TCB10ha <- ggplot(ha10_table, aes(x = TC_B_11_ST, fill = as.factor(Wind01_New))) +
  geom_histogram(binwidth = 0.05, alpha = 0.5, position = "identity") + 
  scale_x_continuous("Normalized Mean Tasseled Cap Brightness") +
  theme(plot.title = element_text(lineheight = 0.5, face = "bold", size = 20), legend.position = c(1,1), legend.justification = c(1,1),
        legend.text = element_text(size = 16, face = "bold"), legend.title = element_blank()) +
  ggtitle("Areas > 10 ha")
# build plot for areas > 15ha
ha15_table = subset(plot_table, Area_ha >= 15)
plot_TCB15ha <- ggplot(ha15_table, aes(x = TC_B_11_ST, fill = as.factor(Wind01_New))) +
  geom_histogram(binwidth = 0.05, alpha = 0.5, position = "identity") + 
  scale_x_continuous("Normalized Mean Tasseled Cap Brightness") +
  theme(plot.title = element_text(lineheight = 0.5, face = "bold", size = 20), legend.position = c(1,1), legend.justification = c(1,1),
        legend.text = element_text(size = 16, face = "bold"), legend.title = element_blank()) +
  ggtitle("Areas > 15 ha")

# Plots for Tasseled Cap Wetness
# build plot for areas > 1ha
ha1_table = subset(plot_table, Area_ha >= 1)
plot_TCW1ha <- ggplot(ha1_table, aes(x = TC_W_11_ST, fill = as.factor(Wind01_New))) +
  geom_histogram(binwidth = 0.05, alpha = 0.5, position = "identity") + 
  scale_x_continuous("Normalized Mean Tasseled Cap Wetness") +
  theme(plot.title = element_text(lineheight = 0.5, face = "bold", size = 20), legend.position = c(1,1), legend.justification = c(1,1),
        legend.text = element_text(size = 16, face = "bold"), legend.title = element_blank()) +
  ggtitle("Areas > 1 ha")
# build plot for areas > 2ha
ha2_table = subset(plot_table, Area_ha >= 2)
plot_TCW2ha <- ggplot(ha2_table, aes(x = TC_W_11_ST, fill = as.factor(Wind01_New))) +
  geom_histogram(binwidth = 0.05, alpha = 0.5, position = "identity") + 
  scale_x_continuous("Normalized Mean Tasseled Cap Wetness") +
  theme(plot.title = element_text(lineheight = 0.5, face = "bold", size = 20), legend.position = c(1,1), legend.justification = c(1,1),
        legend.text = element_text(size = 16, face = "bold"), legend.title = element_blank()) +
  ggtitle("Areas > 2 ha")
# build plot for areas > 5ha
ha5_table = subset(plot_table, Area_ha >= 5)
plot_TCW5ha <- ggplot(ha5_table, aes(x = TC_W_11_ST, fill = as.factor(Wind01_New))) +
  geom_histogram(binwidth = 0.05, alpha = 0.5, position = "identity") + 
  scale_x_continuous("Normalized Mean Tasseled Cap Wetness") +
  theme(plot.title = element_text(lineheight = 0.5, face = "bold", size = 20), legend.position = c(1,1), legend.justification = c(1,1),
        legend.text = element_text(size = 16, face = "bold"), legend.title = element_blank()) +
  ggtitle("Areas > 5 ha")
# build plot for areas > 10ha
ha10_table = subset(plot_table, Area_ha >= 10)
plot_TCW10ha <- ggplot(ha10_table, aes(x = TC_W_11_ST, fill = as.factor(Wind01_New))) +
  geom_histogram(binwidth = 0.05, alpha = 0.5, position = "identity") + 
  scale_x_continuous("Normalized Mean Tasseled Cap Wetness") +
  theme(plot.title = element_text(lineheight = 0.5, face = "bold", size = 20), legend.position = c(1,1), legend.justification = c(1,1),
        legend.text = element_text(size = 16, face = "bold"), legend.title = element_blank()) +
  ggtitle("Areas > 10 ha")
# build plot for areas > 15ha
ha15_table = subset(plot_table, Area_ha >= 15)
plot_TCW15ha <- ggplot(ha15_table, aes(x = TC_W_11_ST, fill = as.factor(Wind01_New))) +
  geom_histogram(binwidth = 0.05, alpha = 0.5, position = "identity") + 
  scale_x_continuous("Normalized Mean Tasseled Cap Wetness") +
  theme(plot.title = element_text(lineheight = 0.5, face = "bold", size = 20), legend.position = c(1,1), legend.justification = c(1,1),
        legend.text = element_text(size = 16, face = "bold"), legend.title = element_blank()) +
  ggtitle("Areas > 15 ha")

# Plots for Band5-Reflectance
# build plot for areas > 1ha
ha1_table = subset(plot_table, Area_ha >= 1)
plot_RB51ha <- ggplot(ha1_table, aes(x = R_B5_11_ST, fill = as.factor(Wind01_New))) +
  geom_histogram(binwidth = 0.05, alpha = 0.5, position = "identity") + 
  scale_x_continuous("Normalized Mean Band05-reflectance") +
  theme(plot.title = element_text(lineheight = 0.5, face = "bold", size = 20), legend.position = c(1,1), legend.justification = c(1,1),
        legend.text = element_text(size = 16, face = "bold"), legend.title = element_blank()) +
  ggtitle("Areas > 1 ha")
# build plot for areas > 2ha
ha2_table = subset(plot_table, Area_ha >= 2)
plot_RB52ha <- ggplot(ha2_table, aes(x = R_B5_11_ST, fill = as.factor(Wind01_New))) +
  geom_histogram(binwidth = 0.05, alpha = 0.5, position = "identity") + 
  scale_x_continuous("Normalized Mean Band05-reflectance") +
  theme(plot.title = element_text(lineheight = 0.5, face = "bold", size = 20), legend.position = c(1,1), legend.justification = c(1,1),
        legend.text = element_text(size = 16, face = "bold"), legend.title = element_blank()) +
  ggtitle("Areas > 2 ha")
# build plot for areas > 5ha
ha5_table = subset(plot_table, Area_ha >= 5)
plot_RB55ha <- ggplot(ha5_table, aes(x = R_B5_11_ST, fill = as.factor(Wind01_New))) +
  geom_histogram(binwidth = 0.05, alpha = 0.5, position = "identity") + 
  scale_x_continuous("Normalized Mean Band05-reflectance") +
  theme(plot.title = element_text(lineheight = 0.5, face = "bold", size = 20), legend.position = c(1,1), legend.justification = c(1,1),
        legend.text = element_text(size = 16, face = "bold"), legend.title = element_blank()) +
  ggtitle("Areas > 5 ha")
# build plot for areas > 10ha
ha10_table = subset(plot_table, Area_ha >= 10)
plot_RB510ha <- ggplot(ha10_table, aes(x = R_B5_11_ST, fill = as.factor(Wind01_New))) +
  geom_histogram(binwidth = 0.05, alpha = 0.5, position = "identity") + 
  scale_x_continuous("Normalized Mean Band05-reflectance") +
  theme(plot.title = element_text(lineheight = 0.5, face = "bold", size = 20), legend.position = c(1,1), legend.justification = c(1,1),
        legend.text = element_text(size = 16, face = "bold"), legend.title = element_blank()) +
  ggtitle("Areas > 10 ha")
# build plot for areas > 15ha
ha15_table = subset(plot_table, Area_ha >= 15)
plot_RB515ha <- ggplot(ha15_table, aes(x = R_B5_11_ST, fill = as.factor(Wind01_New))) +
  geom_histogram(binwidth = 0.05, alpha = 0.5, position = "identity") + 
  scale_x_continuous("Normalized Mean Band05-reflectance") +
  theme(plot.title = element_text(lineheight = 0.5, face = "bold", size = 20), legend.position = c(1,1), legend.justification = c(1,1),
        legend.text = element_text(size = 16, face = "bold"), legend.title = element_blank()) +
  ggtitle("Areas > 15 ha")

# plot the three graphs next to each other
png("d:/Histo_BrightnessSize.png", width=10000,height=6000,res=300)
grid.arrange(arrangeGrob(plot_TCB1ha, plot_TCB2ha, plot_TCB5ha, plot_TCB10ha, plot_TCB15ha,
                         plot_TCW1ha, plot_TCW2ha, plot_TCW5ha, plot_TCW10ha, plot_TCW15ha,
                         plot_RB51ha, plot_RB52ha, plot_RB55ha, plot_RB510ha, plot_RB515ha,
                         nrow = 3))
dev.off()

