# Libs
library(ggplot2)

# Import data
fe_data <- readRDS('data/joined_fe_data.rds')

# Filter to only scored documents
fe_data <- subset(fe_data, !(is.na(scrutiny_score) | is.na(majority_author)))

## FIGURE 1: Scatterplot
ggplot(data = fe_data, aes(x = ideology, y = scrutiny_score)) +
 # ggtitle('Opinion Ideology and Scrutiny Language') +
  xlab('Ideology of Opinion Author') +
  ylab('Opinion Scrutiny Score') +
  theme_minimal() +
  theme(plot.title = element_text(hjust = 0.5, size = 18)) +
  theme(axis.text = element_text(size = 20)) +
  theme(axis.title = element_text(size = 28)) +
  geom_point(aes(x = ideology, y = scrutiny_score), color = 'black', pch = 21, fill = '#D55E00', size = 6) +
  geom_smooth(method = lm)

ggsave(filename = 'scatterplot.svg', width = 20, height = 10)