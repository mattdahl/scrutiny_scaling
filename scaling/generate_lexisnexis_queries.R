## Libs
library(dplyr)

## Data
fe_data = readRDS('data/normalized_fe_data.rds')

## Functions
# Gets unique citations from dataframe
# Uses Lawyer's Edition (LED) instead of the U.S. reporter, since some of the latter are missing
get_citations = function (dataframe) {
  return(as.character(unique(dataframe$LED)))
}

# Rewrites citations as full Lawyer's Edition citation strings
rewrite_citations = function (citations) {
  tokenized_citations = strsplit(citations, split = '/')
  tokenized_citations = lapply(tokenized_citations, as.numeric)
  citation_strings = c()
  for (citation in tokenized_citations) {
    citation_strings = c(citation_strings, paste('cite(', citation[1], ' L. Ed. 2d ', citation[2], ')', sep = ''))
  }
  return(citation_strings)
}

# Creates a search string suitable for LexisNexis
create_query_string = function (citation_strings) {
  return(paste(citation_strings, collapse = ' OR ', sep = ''))
}

## Script
# Partition by content category
cb_data = filter(fe_data, TTRACKS4 == 1)  # Content-based
cn_data = filter(fe_data, TTRACKS4 == 2)  # Content-neutral
lp_data = filter(fe_data, TTRACKS4 == 3)  # Less-protected
nm_data = filter(fe_data, TTRACKS4 == 4)  # Threshold not met

# Get citation strings, rewrite them, and transform them into LexisNexis query strings
cb_query_string = create_query_string(rewrite_citations(get_citations(cb_data)))
cn_query_string = create_query_string(rewrite_citations(get_citations(cn_data)))
lp_query_string = create_query_string(rewrite_citations(get_citations(lp_data)))
nm_query_string = create_query_string(rewrite_citations(get_citations(nm_data)))

# Feed these queries manually into LexisNexis (no API access)
print('Content-based cases:')
print(cb_query_string)

print('Content-neutral cases:')
print(cn_query_string)

print('Less-protected cases:')
print(lp_query_string)

print('Not-met cases:')
print(nm_query_string)