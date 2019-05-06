#!/usr/bin/env python3
import os

# Base file paths
BASE_DIRECTORY = '/Users/mattdahl/Documents/nd/research/projects/scrutiny_scaling/'

# Corpus
CORPUS_DIRECTORY_RAW = os.path.join(BASE_DIRECTORY, 'data/corpus/raw')
CORPUS_DIRECTORY_TRAIN = os.path.join(BASE_DIRECTORY, 'data/corpus/preprocessed/train/')
CORPUS_DIRECTORY_DEV = os.path.join(BASE_DIRECTORY, 'data/corpus/preprocessed/dev/')

# Stopwords
STOPWORDS_FILE_CASE_FACTORS = os.path.join(BASE_DIRECTORY, 'data/stopwords/case_factors.txt')
STOPWORDS_FILE_JUSTICES = os.path.join(BASE_DIRECTORY, 'data/stopwords/justices.txt')

# Models
MODELS_DIRECTORY = os.path.join(BASE_DIRECTORY, 'scaling/models')

# Scores
SCORES_DIRECTORY = os.path.join(BASE_DIRECTORY, 'data/scores')
