#!/usr/bin/env python3
from corpus import PickledCorpusReader, CorpusLoader

import os
import csv
import dill as pickle
import numpy as np


class Scorer(object):
    def __init__(self):
        self.MODEL_DIRECTORY = '/Users/mattdahl/Documents/nd/research/projects/scrutiny_scaling/models'
        self.SCORES_DIRECTORY = '/Users/mattdahl/Documents/nd/research/projects/scrutiny_scaling/scores'
        self.pipeline = self._load_pipeline()
        self.categories = ['CB', 'CN', 'LP']
        self.corpus_loader = CorpusLoader(PickledCorpusReader(dev=True), 1, shuffle=False, categories=self.categories)
        self.scores = []

    def _load_pipeline(self):
        with open(os.path.join(self.MODEL_DIRECTORY, self.MODEL_NAME + '.pickle'), 'rb') as file:
            return pickle.load(file)

    def save(self):
        X_dev_ids = self.corpus_loader.fileids()

        with open(os.path.join(self.SCORES_DIRECTORY, self.MODEL_NAME + '.csv'), 'w') as file:
            writer = csv.writer(file, delimiter=',')
            for i, score in enumerate(self.scores):
                writer.writerow([X_dev_ids[i], score])


class ClassificationScorer(Scorer):
    def __init__(self, model_name):
        self.MODEL_NAME = model_name
        super().__init__()

    def score(self):
        X_dev = self.corpus_loader.documents()
        y_hat_probabilities = np.array(self.pipeline.predict_proba(X_dev))
        score_weights = np.array([3, 2, 1])  # CB, CN, LP
        self.scores = y_hat_probabilities.dot(score_weights)


class RegressionScorer(Scorer):
    def __init__(self, model_name):
        self.MODEL_NAME = model_name
        super().__init__()

    def score(self):
        X_dev = self.corpus_loader.documents()
        y_hat = self.pipeline.predict(X_dev)
        self.scores = y_hat
