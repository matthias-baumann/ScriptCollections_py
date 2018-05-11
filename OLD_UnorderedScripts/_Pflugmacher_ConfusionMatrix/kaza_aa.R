
code_dir <- 'W:/pflugmacher_aa_code/pflugmacher_aa_code/'
data_dir <- 'W:/pflugmacher_aa_code/pflugmacher_aa_code/'

# load code
source(paste(code_dir, 'aa_card.R', sep=''))
source(paste(code_dir, 'aa_confusion_matrix.R', sep=''))
source(paste(code_dir, 'aa_selection_probability.R', sep=''))

# read data
ds <- read.csv(paste(data_dir, 'samples.csv', sep=''))
dw <- read.csv(paste(data_dir, 'weights.csv', sep='')) 

# recode 0 stratum to 2016
# ds$Stratum[ds$Stratum==0] <- 2016

# 255 non-cropland
# 2016 stable cropland
dw$stratum_weights <- dw$stratum/ sum(dw$stratum)



# calculate inclusion probabilities
dw_stratum <- dw[dw$stratum > 0,]
ds$selection_probabilities <- aa_selection_probability(as.integer(ds$Stratum), dw_stratum[,c('class', 'stratum_weights')])

# create adjusted error matrix
cm_unadjusted <- aa_confusion_matrix(ds$Reference, ds$Classification)
cma <- aa_confusion_matrix(ds$Reference, ds$Classification, prob=ds$selection_probabilities)

# estimate accuracy
aa <- aa_card(cma, confusion_matrix = TRUE)

# overall accuracy
aa$accuracy

# accuracy statistics
aa$stats


############################################################################################################
# relax temporal matching requirement +/- 1 year
# not area proportions are not correct anymore, since the map class are treated as fuzzy

ds$mapclass_fix <- ifelse(abs(ds$Classification-ds$Reference) <= 1, ds$Reference, ds$Classification)

# construct error matrix
cma_fix <- aa_confusion_matrix(ds$Reference, ds$mapclass_fix, prob=ds$selection_probabilities)

# estimate accuracy
aa_fix <- aa_card(cma_fix, confusion_matrix = TRUE)


aa_fix$accuracy

aa_fix$stats
