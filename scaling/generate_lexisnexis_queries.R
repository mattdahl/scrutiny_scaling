## Libs
library(dplyr)

## Data
bog_data = readRDS('data/normalized_bog_data.rds')

## Functions
# Rewrites citations as full Lawyer's Edition citation strings, wrapped in 'cite()' strings
# Uses Lawyer's Edition instead of the U.S. reporter, since some of the latter are missing
rewrite_citations = function (citation_data) {
  citation_data$tokenized = lapply(strsplit(as.character(citation_data$led), split = '/'), as.numeric)

  citation_data$string = by(citation_data, 1:nrow(citation_data), function (citation) {
    reporter = ''
    if (citation$term <= 1955) {
      reporter = ' L. Ed. '
    }
    else if (citation$term >= 1956) {
      reporter = ' L. Ed. 2d '
    }
    paste('cite(', citation$tokenized[[1]][1], reporter, citation$tokenized[[1]][2], ')', sep = '')
  })
  
  return(citation_data)
}

# Creates a search string suitable for LexisNexis
create_query_string = function (citation_data) {
  return(paste(citation_data$string, collapse = ' OR ', sep = ''))
}

## Script
# Partition by content category
cb_data = bog_data %>% filter(cb == TRUE) %>% select(led, term) %>% distinct()  # Content-based
cn_data = bog_data %>% filter(cn == TRUE) %>% select(led, term) %>% distinct()  # Content-neutral
lp_data = bog_data %>% filter(lp == TRUE) %>% select(led, term) %>% distinct()  # Less-protected

# Get citation strings, rewrite them, and transform them into LexisNexis query strings
cb_query_string1 = create_query_string(rewrite_citations(cb_data[1:90,]))
cb_query_string2 = create_query_string(rewrite_citations(cb_data[91:180,]))
cb_query_string3 = create_query_string(rewrite_citations(cb_data[181:270,]))
cb_query_string4 = create_query_string(rewrite_citations(cb_data[271:312,]))
cn_query_string = create_query_string(rewrite_citations(cn_data))
lp_query_string1 = create_query_string(rewrite_citations(lp_data[1:60,]))
lp_query_string2 = create_query_string(rewrite_citations(lp_data[61:120,]))
lp_query_string3 = create_query_string(rewrite_citations(lp_data[121:169,]))

# Feed these queries manually into LexisNexis (no API access)