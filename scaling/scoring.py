#!/usr/bin/env python3
from corpus import PickledCorpusReader, CorpusLoader
from settings import MODELS_DIRECTORY, SCORES_DIRECTORY

import os
import csv
import dill as pickle
import numpy as np

from scipy import stats


class Scorer(object):
    def __init__(self):
        self.pipeline = self._load_pipeline()
        self.categories = ['CB', 'CN', 'LP']
        self.corpus_loader = CorpusLoader(PickledCorpusReader(dev=True), 1, shuffle=False, categories=self.categories)
        self.scores = []

    def _load_pipeline(self):
        with open(os.path.join(MODELS_DIRECTORY, self.model_name + '.pickle'), 'rb') as file:
            return pickle.load(file)

    def save(self):
        X_dev_fileids = self.corpus_loader.fileids()
        citations = [fileid.split('-')[1] for fileid in X_dev_fileids]

        y_dev = self._map_scores(self.corpus_loader.labels())

        with open(os.path.join(SCORES_DIRECTORY, self.model_name + '.csv'), 'w') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerow(['fileid', 'citation', 'y_dev', 'scrutiny_score'])
            for i, score in enumerate(self.scores):
                writer.writerow([X_dev_fileids[i], citations[i], y_dev[i], score])


class ClassificationScorer(Scorer):
    def __init__(self, model_name):
        self.model_name = model_name
        super().__init__()

    def score(self):
        X_dev = self.corpus_loader.documents()
        y_hat_probabilities = np.array(self.pipeline.predict_proba(X_dev))
        score_weights = np.array([3, 2, 1])  # CB, CN, LP
        dot_product = y_hat_probabilities.dot(score_weights)
        standardized = stats.zscore(dot_product)

        self.scores = standardized


class RegressionScorer(Scorer):
    def __init__(self, model_name):
        self.model_name = model_name
        super().__init__()

    def score(self):
        X_dev = self.corpus_loader.documents()
        y_hat = self.pipeline.predict(X_dev)
        standardized = stats.zscore(y_hat)

        self.scores = standardized
