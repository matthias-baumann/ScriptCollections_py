################################################################################################################################################
#### LOAD THE REQUIRED PACKAGES ####
library(ggplot2)
library(grDevices)
library(gridExtra)
library(RGraphics)
##################################################################################################################################################
#### BUILD THE PLOTS FOR FOOTPRINT 026027 ####
# LOAD RAW-TABLE AND DEFINE MMU
RAW_table_026027 = read.table(file.choose(), header = T)
table_026027 = subset(RAW_table_026027, Area_m2 > 5400)

# remove "validation == 3", because it is outside the classified area
table_026027 = subset(table_026027, Validation != 3)

# Create subset with the AREA-Values, convert areas into ha
plot_table_026027 = subset(table_026027, , c(Area_m2, Validation, Classification))
plot_table_026027$Area_ha = plot_table_026027$Area_m2 / 10000

# GET THE LEVELS FROM THE AREA_VARIABLE
pol_sizes = levels(as.factor(plot_table_026027$Area_ha))
n = length(pol_sizes)

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

# now loop though the indices
for (i in 1:length(ll)){
  ll_size = pol_sizes[i]
  ul_size = pol_sizes[i+1]
  # subset the table
  tmp_all = subset(plot_table_026027, Area_ha >= as.numeric(ll_size) & Area_ha <= as.numeric(ul_size))
  tmp_wind = subset(plot_table_026027, Area_ha >= as.numeric(ll_size) & Area_ha <= as.numeric(ul_size) & Validation == 1)
  tmp_other = subset(plot_table_026027, Area_ha >= as.numeric(ll_size) & Area_ha <= as.numeric(ul_size) & Validation == 0)
  # Calculate the proportions --> ALL
  tmp_all$eval = ifelse(tmp_all$Validation == tmp_all$Classification,1,0)
  p_all = sum(tmp_all$eval) / length(tmp_all$Classification)
  # --> Windfall
  tmp_wind$eval = ifelse(tmp_wind$Validation == tmp_wind$Classification,1,0)
  p_wind = sum(tmp_wind$eval) / length(tmp_wind$Classification)
  # --> Other
  tmp_other$eval = ifelse(tmp_other$Validation == tmp_other$Classification,1,0)
  p_other = sum(tmp_other$eval) / length(tmp_other$Classification)   
  # Write into output-array
  sizes = c(sizes,as.numeric(ul_size))
  prop_all = c(prop_all, as.numeric(p_all))
  numPol_all = c(numPol_all, as.numeric(length(tmp_all$Classification)))
  prop_wind = c(prop_wind, as.numeric(p_wind))
  numPol_wind = c(numPol_wind, as.numeric(length(tmp_wind$Classification)))  
  prop_other = c(prop_other, as.numeric(p_other))
  numPol_other = c(numPol_other, as.numeric(length(tmp_other$Classification))) 
}

# concatenate output values into dataframe
out_026027 = data.frame(cbind(sizes, prop_all, numPol_all, prop_wind, numPol_wind, prop_other, numPol_other))
out_026027$px = (out_026027$sizes * 10000) / 900
colnames(out_026027) = c("Pol_Size_ha", "Prop_Cor_All", "Num_Pol_All", "Prop_Cor_Wind", "Num_Pol_Wind", "Prop_Cor_Other", "Num_Pol_Other", "PX")

# build plot for both classes together
plot_all_026027 <- ggplot(out_026027, aes(x = Pol_Size_ha, y = Prop_Cor_All)) +
  geom_point(size = 2) + 
  stat_smooth(method = "loess", se = TRUE, level = 0.95, geom = "smooth", size = 1) + 
  scale_x_continuous("Size of disturbance patch [ha]") + 
  scale_y_continuous("Proportion Correctly classified Polygons", limits = c(0.4,1)) +
  ggtitle("Minnesota (USA)\n'Windfall' + 'Other'") +
  theme(plot.title = element_text(lineheight = 1, face = "bold", size = 22, vjust = 1.4),
        axis.title.x = element_text(family = "sans", size = 20, vjust = 0.01),
        axis.title.y = element_text(family = "sans", size = 20, vjust = 0.3),
        axis.text.x = element_text(family = "sans", size = 24),
        axis.text.y = element_text(family = "sans", size = 24))
   
# build the same graph with windfall only
plot_wind_026027 <- ggplot(out_026027, aes(x = Pol_Size_ha, y = Prop_Cor_Wind)) +
  geom_point(size = 2) + 
  stat_smooth(method = "loess", se = TRUE, level = 0.95, geom = "smooth", size = 1) + 
  scale_x_continuous("Size of disturbance patch [ha]") + 
  scale_y_continuous("Proportion Correctly classified Polygons", limits = c(0.4,1)) +
  ggtitle("Minnesota (USA)\n'Windfall'") +
  theme(plot.title = element_text(lineheight = 1, face = "bold", size = 22, vjust = 1.4),
        axis.title.x = element_text(family = "sans", size = 20, vjust = 0.01),
        axis.title.y = element_text(family = "sans", size = 20, vjust = 0.3),
        axis.text.x = element_text(family = "sans", size = 24),
        axis.text.y = element_text(family = "sans", size = 24))

# build the same graph with 'other' only
plot_other_026027 <- ggplot(out_026027, aes(x = Pol_Size_ha, y = Prop_Cor_Other)) +
  geom_point(size = 2) + 
  stat_smooth(method = "loess", se = TRUE, level = 0.95, geom = "smooth", size = 1) + 
  scale_x_continuous("Size of disturbance patch [ha]") + 
  scale_y_continuous("Proportion Correctly classified Polygons", limits = c(0.4,1)) +
  ggtitle("Minnesota (USA)\n'Other'") +
  theme(plot.title = element_text(lineheight = 1, face = "bold", size = 22, vjust = 1.4),
        axis.title.x = element_text(family = "sans", size = 20, vjust = 0.01),
        axis.title.y = element_text(family = "sans", size = 20, vjust = 0.3),
        axis.text.x = element_text(family = "sans", size = 24),
        axis.text.y = element_text(family = "sans", size = 24))



##################################################################################################################################################
#### BUILD THE PLOTS FOR FOOTPRINT 177019 ####
# LOAD RAW-TABLE AND DEFINE MMU
RAW_table_177019 = read.table(file.choose(), header = T)
table_177019 = subset(RAW_table_177019, Area_m2 > 5400)


# Create subset with the AREA-Values, convert areas into ha
plot_table_177019 = subset(table_177019, , c(Area_m2, Validation, Classification))
plot_table_177019$Area_ha = plot_table_177019$Area_m2 / 10000

# GET THE LEVELS FROM THE AREA_VARIABLE
pol_sizes = levels(as.factor(plot_table_177019$Area_ha))
n = length(pol_sizes)

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

# now loop though the indices
for (i in 1:length(ll)){
  ll_size = pol_sizes[i]
  ul_size = pol_sizes[i+1]
  # subset the table
  tmp_all = subset(plot_table_177019, Area_ha >= as.numeric(ll_size) & Area_ha <= as.numeric(ul_size))
  tmp_wind = subset(plot_table_177019, Area_ha >= as.numeric(ll_size) & Area_ha <= as.numeric(ul_size) & Validation == 1)
  tmp_other = subset(plot_table_177019, Area_ha >= as.numeric(ll_size) & Area_ha <= as.numeric(ul_size) & Validation == 0)
  # Calculate the proportions --> ALL
  tmp_all$eval = ifelse(tmp_all$Validation == tmp_all$Classification,1,0)
  p_all = sum(tmp_all$eval) / length(tmp_all$Classification)
  # --> Windfall
  tmp_wind$eval = ifelse(tmp_wind$Validation == tmp_wind$Classification,1,0)
  p_wind = sum(tmp_wind$eval) / length(tmp_wind$Classification)
  # --> Other
  tmp_other$eval = ifelse(tmp_other$Validation == tmp_other$Classification,1,0)
  p_other = sum(tmp_other$eval) / length(tmp_other$Classification)   
  # Write into output-array
  sizes = c(sizes,as.numeric(ul_size))
  prop_all = c(prop_all, as.numeric(p_all))
  numPol_all = c(numPol_all, as.numeric(length(tmp_all$Classification)))
  prop_wind = c(prop_wind, as.numeric(p_wind))
  numPol_wind = c(numPol_wind, as.numeric(length(tmp_wind$Classification)))  
  prop_other = c(prop_other, as.numeric(p_other))
  numPol_other = c(numPol_other, as.numeric(length(tmp_other$Classification))) 
}

# concatenate output values into dataframe
out_177019 = data.frame(cbind(sizes, prop_all, numPol_all, prop_wind, numPol_wind, prop_other, numPol_other))
out_177019$px = (out_177019$sizes * 10000) / 900
colnames(out_177019) = c("Pol_Size_ha", "Prop_Cor_All", "Num_Pol_All", "Prop_Cor_Wind", "Num_Pol_Wind", "Prop_Cor_Other", "Num_Pol_Other", "PX")

# build plot for both classes together
plot_all_177019 <- ggplot(out_177019, aes(x = Pol_Size_ha, y = Prop_Cor_All)) +
  geom_point(size = 2) + 
  stat_smooth(method = "loess", se = TRUE, level = 0.95, geom = "smooth", size = 1) + 
  scale_x_continuous("Size of disturbance patch [ha]") + 
  scale_y_continuous("Proportion Correctly classified Polygons", limits = c(0.4,1)) +
  ggtitle("Russia\n'Windfall' + 'Other'") +
  theme(plot.title = element_text(lineheight = 1, face = "bold", size = 22, vjust = 1.4),
        axis.title.x = element_text(family = "sans", size = 20, vjust = 0.01),
        axis.title.y = element_text(family = "sans", size = 20, vjust = 0.3),
        axis.text.x = element_text(family = "sans", size = 24),
        axis.text.y = element_text(family = "sans", size = 24))

# build the same graph with windfall only
plot_wind_177019 <- ggplot(out_177019, aes(x = Pol_Size_ha, y = Prop_Cor_Wind)) +
  geom_point(size = 2) + 
  stat_smooth(method = "loess", se = TRUE, level = 0.95, geom = "smooth", size = 1) + 
  scale_x_continuous("Size of disturbance patch [ha]") + 
  scale_y_continuous("Proportion Correctly classified Polygons", limits = c(0.4,1)) +
  ggtitle("Russia\n'Windfall'") +
  theme(plot.title = element_text(lineheight = 1, face = "bold", size = 22, vjust = 1.4),
        axis.title.x = element_text(family = "sans", size = 20, vjust = 0.01),
        axis.title.y = element_text(family = "sans", size = 20, vjust = 0.3),
        axis.text.x = element_text(family = "sans", size = 24),
        axis.text.y = element_text(family = "sans", size = 24))

# build the same graph with 'other' only
plot_other_177019 <- ggplot(out_177019, aes(x = Pol_Size_ha, y = Prop_Cor_Other)) +
  geom_point(size = 2) + 
  stat_smooth(method = "loess", se = TRUE, level = 0.95, geom = "smooth", size = 1) + 
  scale_x_continuous("Size of disturbance patch [ha]") + 
  scale_y_continuous("Proportion Correctly classified Polygons", limits = c(0.4,1)) +
  ggtitle("Russia\n'Other'") +
  theme(plot.title = element_text(lineheight = 1, face = "bold", size = 22, vjust = 1.4),
        axis.title.x = element_text(family = "sans", size = 20, vjust = 0.01),
        axis.title.y = element_text(family = "sans", size = 20, vjust = 0.3),
        axis.text.x = element_text(family = "sans", size = 24),
        axis.text.y = element_text(family = "sans", size = 24))

##################################################################################################################################################
#### PUT THE PLOTS INTO ONE GRAPHIC, TOP ROW 177019, BOTTOM ROW 026027 ####

# plot the three graphs next to each other
png("d:/accuracy_SizeHA.png", width=6000,height=4000,res=300)
grid.arrange(arrangeGrob(plot_all_177019, plot_wind_177019, plot_other_177019,
                         plot_all_026027, plot_wind_026027, plot_other_026027,
                         nrow = 2))
dev.off()


