# Import Bartels and O'Green's dataset
bog_data = get(load('data/bog_data.RData'))

# Re-save as RDS file
saveRDS(bog_data, file = 'data/normalized_bog_data.rds')