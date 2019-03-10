# Libs
library(haven)
library(readr)
library(plyr)
library(dplyr)
library(lme4)

# Load data
fe_data = readRDS('data/free_expression_data.rds')

# Restrict to post-Grayned cases
fe_data_after_grayned = filter(fe_data, MOSLEY == 1)

# Get citations (in the format '123/0456')
# Use Lawyer's Edition since they are complete (some U.S. citations are missing from this dataset)
citations = as.character(unique(fe_data_after_grayned$LED))

# Rewrite citations as strings suitable for a LexisNexis query
tokenized_citations = strsplit(citations, split = '/')
tokenized_citations = lapply(tokenized_citations, as.numeric)
citation_strings = c()
for (citation in tokenized_citations) {
  citation_strings = c(citation_strings, paste('cite(', citation[1], ' L. Ed. 2d ', citation[2], ')', sep = ''))
}

# Break strings into chunks for easier querying (big queries are slow and possibly rate-limited)
cs1 = citation_strings[1:100]
cs2 = citation_strings[101:200]
cs3 = citation_strings[201:length(citation_strings)]

# Create LexisNexis search queries
search_query1 = paste(cs1, collapse = ' OR ', sep = '')
search_query2 = paste(cs2, collapse = ' OR ', sep = '')
search_query3 = paste(cs3, collapse = ' OR ', sep = '')

# Feed these queries manually into LexisNexis (no API access)