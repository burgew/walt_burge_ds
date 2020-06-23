# R script for generating venn diagrams
# I'm not aware of a robust way of implementing this in python but due to my familiarity with R
# I quickly made a small script to create these specific EDA plots. 

library(gridExtra)
library(ggplot2)
library(venn)
library(data.table)

train_data <- fread("~/Github/w207_FinalProject/data/new_train.csv") # load train data
p1 <- venn(train_data[, .(toxic, severe_toxic, obscene, insult)],ilabels = TRUE, col = "navyblue")
p2 <- venn(train_data[, .(toxic, insult, obscene)])
p3 <- venn(train_data[, .(severe_toxic, insult, obscene)])

