# Libs
library(readr)
library(haven)
library(plyr)
library(dplyr)

# Import data
fe_data <- readRDS('data/normalized_fe_data.rds')
scrutiny_scores <- read_csv('data/scores/Ridge-1557373194.313121.csv')
mq_scores <- read_csv('/Users/mattdahl/Documents/nd/research/data/MartinQuinn_Scores_2018.csv')

# Prune the fe_data
fe_data <- dplyr::select(fe_data,
  us_citation = US,
  led = LED,
  term = TERM,
  scrutiny_level = TTRACKS4,
  speaker_identity = IDENTITY,
  government = GOVERN,
  action = ACTION,
  majority_author = MOW_N
)

# Create normalized citation variable for data merging
rewrite_citation = function (citation) {
  tokenized = lapply(strsplit(citation, split = '/'), as.numeric)
  return(paste(tokenized[[1]][1], '|', tokenized[[1]][2], sep = ''))
}
fe_data$citation <- unlist(lapply(fe_data$us_citation, rewrite_citation))

# Prune the Martin Quinn scores
# Negative = liberal
# Positive = conservative
mq_scores <- dplyr::select(mq_scores,
  term = term,
  justice = justice,
  ideology = post_mn
)

# Invert the ideology values, so now
# Negative = conservative
# Positive = liberal
mq_scores$ideology <- mq_scores$ideology * -1

# Coerce the MQ justice and term variables to doubles and factorize
mq_scores$justice <- factor(as.numeric(mq_scores$justice))
mq_scores$term <- factor(as.numeric(mq_scores$term))

# Prune the scrutiny scores
scrutiny_scores <- dplyr::select(scrutiny_scores,
  citation = citation,
  scrutiny_score = scrutiny_score
  y_dev = y_dev
)

# Consolidate data (before, each row represents a vote; after, each row represents an opinion)
fe_data <- dplyr::distinct(fe_data)

# Join the fe_data with the MQ scores for the author of each majority opinion
fe_data <- dplyr::left_join(fe_data, mq_scores, by = c('majority_author' = 'justice', 'term' = 'term'))

# Join the fe_data with the scrutiny scores for each opinion
fe_data <- dplyr::left_join(fe_data, scrutiny_scores, by = c('citation' = 'citation'))

# Save the joined data
saveRDS(fe_data, file = 'data/joined_fe_data.rds')