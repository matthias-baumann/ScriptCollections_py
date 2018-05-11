#' Calculate selection probability
#'
#' @title aa_selection_probability
#' @description Calculates selection probability of a stratified random sample
#' @param samples sample vector of stratum labels
#' @param strata_weights two-column array or data frame with stratum labels (1) and stratum weights (2)
#' @return vector of selection probabilities
#' @author Dirk Pflugmacher
#' 

aa_selection_probability <- function(samples, strata_weights) {
  
  n_samples=length(samples)
  
  if (class(strata_weights[,1]) != class(samples)) {
    message('Mismatch in data type.')
    message(paste('samples is of type',class(samples)))
    message(paste('stratum is of type',class(strata_weights[,1])))
    return(invisible(NULL))
  }
  
  df <- data.frame(samples=samples, rowid=1:length(samples))
  
  df <- merge(df, strata_weights, by.x=1, by.y=1)
  if (nrow(df) != n_samples) {
    message('Error merging samples and strata')
    message(paste('Number of rows changed to',nrow(df)))
    return(invisible(NULL))
  }
  
  temp <- aggregate(df[,3] ~ df$samples, FUN=function(x) max(x)/length(x))
  
  df <- merge(df, temp, by.x=1, by.y=1)
  if (nrow(df) != n_samples) {
    message('Error merging samples and sampling proportions.')
    message(paste('Number of rows changed to',nrow(df)))
    return(invisible(NULL))
  }
  
  if (sum(df[,4]) < 0.99) message(paste('Total sample probability','=',sum(df[,4])))
  
  return(df[order(df$rowid),4])
  
}