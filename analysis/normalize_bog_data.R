# Libs
library(haven)
library(readr)
library(plyr)
library(dplyr)
library(lme4)

# Import Bartels and O'Green's dataset
bog_data = get(load('data/bog_data.RData'))

# Filter to only include content-neutral and content-based cases
bog_data <- filter(bog_data, (cn == TRUE | cb == TRUE))

# Save the normalized data
saveRDS(bog_data, file = 'data/normalized_bog_data.rds')