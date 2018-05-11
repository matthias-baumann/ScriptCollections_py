#### LOAD PACKAGES, NEEDED TO CREATE THE PLOTS ####
library(ggplot2)
library(gregmisc)

#### LOAD DATA TABLE AND SET INTIAL WORKSPACE AND EXCLUDE DISTURBANCES THAT ARE SMALLER THAN 7 PIXEL ####
RAW_table = read.table(file.choose(), header = T)
table = subset(RAW_table, Area_m2 > 5400)

######################################################################
#### BUILD THE BOXPLOT ####

ggplot(table, aes(x = log(log(Area_m2)))) +
  geom_density(alpha = 0.5, position = "identity")




plot <- ggplot(table, aes(x = R_B5_11_ST, fill = as.factor(Validation))) +
        geom_density(alpha = 0.5, position = "identity") +
        scale_fill_manual(values = c("#0000FF", "#FF4040")) +
        scale_x_continuous("Normalized Band5-Reflectance") + 
        scale_y_continuous("") + 
        theme(plot.title = element_text(lineheight = 1, face = "bold", size = 20, vjust = 1.4),
            axis.title.x = element_text(family = "sans", size = 15, vjust = 0.01),
            #axis.title.y = element_text(family = "sans", size = 15, vjust = 0.3),
            axis.text.x = element_text(family = "sans", size = 15),
            axis.text.y = element_text(family = "sans", size = 15)
            )

plot


png("d:/Scheme.png", width=8000,height=4000,res=600)
plot
dev.off()





