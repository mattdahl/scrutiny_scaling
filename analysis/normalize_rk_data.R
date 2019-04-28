# Libs
library(haven)
library(readr)
library(plyr)
library(dplyr)
library(lme4)

# Import Richards and Kritzer's database
dataset = read_sav('data/rk_data.sav')
mq_scores <- read_csv('/Users/mattdahl/Documents/nd/research/data/MartinQuinn_Scores_2018.csv')

# Select only cases that present a "free press, free expression, or free speech issue"
# Exclude the Mosley and Grayned cases themselves (MOSLEY < 3)
# Remove an erroneous observation (cf. Bartels) (LED == '115/0447' & JUSTICE == 11)
fe_data <- filter(dataset, FIRSTDE == 1, MOSLEY == 1)
fe_data <- filter(fe_data, !(LED == '115/0447' & JUSTICE == 11))

# Transform VOTING values from [1, 2] to [1, 0], so now
# 1 = pro-expression
# 2 = pro-government
fe_data$VOTING <- fe_data$VOTING - 2
fe_data$VOTING <- fe_data$VOTING * -1

# Prune the Martin Quinn scores
# Negative = liberal
# Positive = conservative
mq_scores <- select(mq_scores, TERM = term, JUSTICE = justice, MQ_IDEOLOGY = post_mn)

# Invert the MQ_IDEOLOGY values, so now
# Negative = conservative
# Positive = liberal
mq_scores$MQ_IDEOLOGY <- mq_scores$MQ_IDEOLOGY * -1

# Remove all the attributes from the RK JUSTICE and TERM variables (for easy merge)
attr(fe_data$JUSTICE, 'class') <- NULL
attr(fe_data$JUSTICE, 'labels') <- NULL
attr(fe_data$JUSTICE, 'format.spss') <- NULL
attr(fe_data$JUSTICE, 'display_width') <- NULL
attr(fe_data$TERM, 'format.spss') <- NULL
attr(fe_data$TERM, 'display_width') <- NULL

# Coerce the MQ justice and term variables to doubles
mq_scores$JUSTICE <- as.numeric(mq_scores$JUSTICE)
mq_scores$TERM <- as.numeric(mq_scores$TERM)

# Normalize the justice ids from RK (since RK used some weird system...)
fe_data$JUSTICE_N <- NA
fe_data$JUSTICE_N[fe_data$JUSTICE == 1] <- 91 # Harlan
fe_data$JUSTICE_N[fe_data$JUSTICE == 2] <- 78 # Black
fe_data$JUSTICE_N[fe_data$JUSTICE == 3] <- 81 # Douglas
fe_data$JUSTICE_N[fe_data$JUSTICE == 4] <- 94 # Stewart
fe_data$JUSTICE_N[fe_data$JUSTICE == 5] <- 98 # TMarshall
fe_data$JUSTICE_N[fe_data$JUSTICE == 6] <- 92 # Brennan
fe_data$JUSTICE_N[fe_data$JUSTICE == 7] <- 95 # White
fe_data$JUSTICE_N[fe_data$JUSTICE == 8] <- 90 # Warren
fe_data$JUSTICE_N[fe_data$JUSTICE == 9] <- 88 # Clark
fe_data$JUSTICE_N[fe_data$JUSTICE == 10] <- 80 # Frankfurter
fe_data$JUSTICE_N[fe_data$JUSTICE == 11] <- 93 # Whittaker
fe_data$JUSTICE_N[fe_data$JUSTICE == 12] <- 86 # Burton
fe_data$JUSTICE_N[fe_data$JUSTICE == 13] <- 79 # Reed
fe_data$JUSTICE_N[fe_data$JUSTICE == 14] <- 97 # Fortas
fe_data$JUSTICE_N[fe_data$JUSTICE == 15] <- 96 # Goldberg
fe_data$JUSTICE_N[fe_data$JUSTICE == 16] <- 89 # Minton
fe_data$JUSTICE_N[fe_data$JUSTICE == 17] <- 84 # Jackson
fe_data$JUSTICE_N[fe_data$JUSTICE == 18] <- 99 # Burger
fe_data$JUSTICE_N[fe_data$JUSTICE == 19] <- 100 # Blackmun
fe_data$JUSTICE_N[fe_data$JUSTICE == 20] <- 101 # Powell
fe_data$JUSTICE_N[fe_data$JUSTICE == 21] <- 102 # Rehnquist
fe_data$JUSTICE_N[fe_data$JUSTICE == 22] <- 103 # Stevens
fe_data$JUSTICE_N[fe_data$JUSTICE == 23] <- 104 # O'Connor
fe_data$JUSTICE_N[fe_data$JUSTICE == 24] <- 105 # Scalia
fe_data$JUSTICE_N[fe_data$JUSTICE == 25] <- 106 # Kennedy
fe_data$JUSTICE_N[fe_data$JUSTICE == 26] <- 107 # Souter
fe_data$JUSTICE_N[fe_data$JUSTICE == 27] <- 108 # Thomas
fe_data$JUSTICE_N[fe_data$JUSTICE == 28] <- 109 # Ginsburg
fe_data$JUSTICE_N[fe_data$JUSTICE == 29] <- 110 # Breyer

# Do the same with the majority opinion writer variable
fe_data$MOW_N <- NA
fe_data$MOW_N[fe_data$MOW == 'BLC'] <- 78
fe_data$MOW_N[fe_data$MOW == 'FRK'] <- 80
fe_data$MOW_N[fe_data$MOW == 'DOUG'] <- 81
fe_data$MOW_N[fe_data$MOW == 'BURT'] <- 86
fe_data$MOW_N[fe_data$MOW == 'CLK'] <- 88
fe_data$MOW_N[fe_data$MOW == 'WAR'] <- 90
fe_data$MOW_N[fe_data$MOW == 'HAR'] <- 91
fe_data$MOW_N[fe_data$MOW == 'BRN'] <- 92
fe_data$MOW_N[fe_data$MOW == 'WHIT'] <- 93 # Whittaker
fe_data$MOW_N[fe_data$MOW == 'STWT'] <- 94
fe_data$MOW_N[fe_data$MOW == 'BW'] <- 95 # White
fe_data$MOW_N[fe_data$MOW == 'MAR'] <- 98
fe_data$MOW_N[fe_data$MOW == 'BURG'] <- 99
fe_data$MOW_N[fe_data$MOW == 'BLKM'] <- 100
fe_data$MOW_N[fe_data$MOW == 'POW'] <- 101
fe_data$MOW_N[fe_data$MOW == 'REHN'] <- 102
fe_data$MOW_N[fe_data$MOW == 'STEV'] <- 103
fe_data$MOW_N[fe_data$MOW == 'OCON'] <- 104
fe_data$MOW_N[fe_data$MOW == 'SCAL'] <- 105
fe_data$MOW_N[fe_data$MOW == 'KEN'] <- 106
fe_data$MOW_N[fe_data$MOW == 'SOUT'] <- 107
fe_data$MOW_N[fe_data$MOW == 'THOM'] <- 108
fe_data$MOW_N[fe_data$MOW == 'GIN'] <- 109
fe_data$MOW_N[fe_data$MOW == 'BRY'] <- 110

# Add the US citations for those that are missing
fe_data$US[fe_data$LED == '129/0118'] <- '512/0136'
fe_data$US[fe_data$LED == '130/0368'] <- '513/0979'
fe_data$US[fe_data$LED == '130/0902'] <- '513/0374'
fe_data$US[fe_data$LED == '138/0585'] <- '521/0457'
fe_data$US[fe_data$LED == '138/0874'] <- '521/0844'
fe_data$US[fe_data$LED == '139/0797'] <- '522/0359'
fe_data$US[fe_data$LED == '140/0759'] <- '523/0574'
fe_data$US[fe_data$LED == '140/0875'] <- '523/0666'
fe_data$US[fe_data$LED == '140/1070'] <- '523/0866'
fe_data$US[fe_data$LED == '141/0500'] <- '524/0569'

# Add the majority opinion writers for those that are missing
fe_data$MOW_N[fe_data$LED == '137/0001'] <- 102 # Rehnquist
fe_data$MOW_N[fe_data$LED == '137/0369'] <- 106 # Kennedy
fe_data$MOW_N[fe_data$LED == '137/0589'] <- 102 # Rehnquist
fe_data$MOW_N[fe_data$LED == '138/0585'] <- 103 # Stevens
fe_data$MOW_N[fe_data$LED == '138/0874'] <- 103 # Stevens
fe_data$MOW_N[fe_data$LED == '139/0797'] <- 105 # Scalia
fe_data$MOW_N[fe_data$LED == '140/0759'] <- 103 # Stevens
fe_data$MOW_N[fe_data$LED == '140/0875'] <- 106 # Kennedy
fe_data$MOW_N[fe_data$LED == '140/1070'] <- 109 # Ginsburg
fe_data$MOW_N[fe_data$LED == '141/0500'] <- 104 # O'Connor
fe_data$MOW_N[fe_data$LED == '037/0993'] <- NA # PER CURIAM
fe_data$MOW_N[fe_data$LED == '041/0842'] <- NA # PER CURIAM
fe_data$MOW_N[fe_data$LED == '041/1033'] <- NA # PER CURIAM
fe_data$MOW_N[fe_data$LED == '046/0659'] <- NA # PER CURIAM
fe_data$MOW_N[fe_data$LED == '062/0607'] <- NA # PER CURIAM
fe_data$MOW_N[fe_data$LED == '063/0413'] <- NA # PER CURIAM
fe_data$MOW_N[fe_data$LED == '068/0489'] <- NA # PER CURIAM
fe_data$MOW_N[fe_data$LED == '120/0669'] <- NA # PER CURIAM

# Normalize the term ids from RK, by incrementing them all by 1900
fe_data$TERM <- fe_data$TERM + 1900

# Join the RK data with the MQ scores for each justice
fe_data <- left_join(fe_data, mq_scores, by = c('JUSTICE_N' = 'JUSTICE', 'TERM' = 'TERM'))

# Factorize the relevant variables
fe_data$TTRACKS4 <- factor(fe_data$TTRACKS4, levels = c(2, 1, 3, 4)) # Base = content-neutral (3)
fe_data$IDENTITY <- factor(fe_data$IDENTITY, levels = c(1, 0, 2, 3, 4, 5, 6, 7, 8)) # Base = other (1)
fe_data$GOVERN <- factor(fe_data$GOVERN, levels = c(5, 0, 1, 2, 3, 4)) # Base = state (5)
fe_data$ACTION <- factor(fe_data$ACTION, levels = c(2, 1, 3, 4, 5, 6, 7)) # Base = civil (2)
fe_data$TERM <- factor(fe_data$TERM)
fe_data$LED <- factor(fe_data$LED)

# Save the normalized data
saveRDS(fe_data, file = 'data/free_expression_data.rds')