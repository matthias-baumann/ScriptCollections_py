library(ggplot2)
library(reshape2)
library(grid)
setwd("W:\\Hab_Structure_Analysis")

#Read the data for the bar charts
hierPartData = read.csv("Hier_Part_Nationwide_All_Ecoregions_For_Auk_For_Fig3.csv")
str(hierPartData)

hierPartData$IC = as.numeric(hierPartData$IC)

str(hierPartData)

levels(hierPartData$Category) = c("Horizontal Composition", "Horizontal Configuration", "Vertical")
#Re-order the ecoregion factor for the graph
levels(hierPartData$Ecoregion)
hierPartData$Ecoregion = factor(hierPartData$Ecoregion, levels(hierPartData$Ecoregion)[c(2,4,3,1)])
#Re-order the guild names for the graph
hierPartData$Guild = factor(hierPartData$Guild, levels(hierPartData$Guild)[c(4,3,2,1)])



#set up a dataframe with the R2 values to annotate the plot
#I had reversed the order of the guilds in the plot, so that "all" would be displayed on top and "Shrubland" at the bottom, so I need to reverse the R2 values similarly
rsqrd = c(rev(c("0.46", "0.70", "0.48","0.27")), rev(c("0.48","0.57","0.63","0.40")), rev(c("0.27","0.47","0.42","0.37")), rev(c("0.14","0.16","0.29","0.08")))
#The x coordinates at which to display the labels
r2_vals$x = rep(c(1, 2, 3, 4), 4)
#the y-coordinates at which to display the labels
r2_vals$y = rep.int(110,16)
#set up an ecoregion variable, which will make sure that the values are printed in the panel for the correct ecoregion
r2_vals$Ecoregion = c(rep("Conterminous United States",4), rep("Great Plains Palouse Dry Steppe",4), rep("Eastern Broadleaf Forest",4), rep("Central Appalachian Broadleaf Forest",4))
#the single quotes ' are included so the numbers are treated as text, otherwise the trailing zeros are dropped
r2_vals$labs = paste("italic(R)^2=='", rsqrd, "'",sep = "")


#Set up the tif file to write this graphic to.
tiff(file='Figures\\Figure_3_HierPart_By_Category_052213.tif', height=9, width=7, res=500, units='in', compression = "lzw")

#Draw the plot  #Note: the order for the four margins is top, right, bottom, left
#The way this works is that you can assign a call to GGPlot to a variable, then keep appending it with other commands, calling it at the end
#start a ggplot, set the Guild as my x-variable, independent contribution (IC) as y-variable, and change the fill color based on "Category"
barPlot = ggplot(hierPartData, aes(x = Guild, y = IC, fill = Category))
#set the color theme to black and white, create a separate panel for each ecoregion, and put the panels in a single column, make the bar graph
barPlot = barPlot + theme_bw() + facet_wrap(~ Ecoregion, ncol = 1) + geom_bar(stat="identity", colour="black", width = 0.85)
#Flip the bar graph to horizontal, label the axes and the categorical variable
barPlot = barPlot + coord_flip() + labs(fill = "Structure Category:", x = "Avian Guild", y = "Independent Contribution of Variable")
#Manually set the colors used to fill the bar graph, put the legend on the bottom
barPlot = barPlot + scale_fill_manual(values=c("#F9F9F9", "#BDBDBD", "#636363"))  + theme(legend.position="bottom")
#set the text color, size, and position for several things.  Give the bar graph black boundaries that show the different variables even if they are the same color
#The "expand_limits" function made the bar graph area wider so that I could have a place to write the R2 value, I manually labeld the axis though so it stops labeling at 100
barPlot = barPlot + theme(axis.title.x = element_text(colour="black", size = 16, hjust=.5, vjust= -0.75,face="plain"),
        axis.title.y = element_text(colour="black", size = 16, hjust=0.5, vjust= 0.25,face="plain"),
        legend.background = element_rect(colour = "black"), legend.margin = unit(0.9, "cm"), strip.text = element_text(size = 12),
        panel.margin = unit(0.35, "cm"), plot.margin = unit(c(1.0, 1.0, 0.2, 1.25), "lines")) + expand_limits(y = c(0, 115)) + scale_y_continuous(breaks=seq(0, 100, 25))

#Add the R2 annotations (The parse = TRUE, will interperet the '^' in the string as superscript
barPlot + geom_text(aes(x, y, label = labs, fill = NULL), data = r2_vals, size = 3.5, parse = T)

#Close Graphic (finish writing the tiff file)
dev.off()
