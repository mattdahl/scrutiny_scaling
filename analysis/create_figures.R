# Libs
library(ggplot2)

# Import data
fe_data <- readRDS('data/joined_fe_data.rds')

## FIGURE 1: Scatterplot
ggplot(data = fe_data, aes(x = ideology, y = scrutiny_score)) +
  ggtitle('Scatterplot') +
  xlab('Ideology of majority opinion writer') +
  ylab('Scrutiny Score') +
  theme_minimal() +
  theme(plot.title = element_text(hjust = 0.5, size = 18)) +
  geom_point(aes(x = ideology, y = scrutiny_score), color = 'black', pch = 21, fill = '#D55E00', size = 3) +
  geom_smooth(method=lm)