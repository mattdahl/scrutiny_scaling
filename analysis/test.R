# Libs
library("MASS")

# Import data
fe_data <- readRDS('data/joined_fe_data.rds')

# Filter to only scored documents
fe_data <- subset(fe_data, !(is.na(scrutiny_score) | is.na(majority_author)))

# Regression model
base_formula <- c(
  'factor(scrutiny_level, levels = c(3, 1, 2, 4))', # Base = less-protected (3)
  'factor(speaker_identity, levels = c(1, 0, 2, 3, 4, 5, 6, 7, 8))', # Base = other (1)
  'factor(government, levels = c(5, 0, 1, 2, 3, 4))', # Base = state (5)
  'factor(action, levels = c(2, 1, 3, 4, 5, 6, 7))', # Base = civil (2)
  'ideology'
)

model <- lm(
  paste('scrutiny_score ~', paste(base_formula, collapse = '+')),
  data = fe_data
)

model2 <- lm(
  scrutiny_score ~ ideology,
  data = fe_data
)

# Robust rlm
model3 <- rlm(
  scrutiny_score ~ ideology,
  data = fe_data
)