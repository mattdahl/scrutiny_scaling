#!/usr/bin/env python3
from normalization import OpinionNormalizer
from corpus import PickledCorpusReader, CorpusLoader

import os
import pickle
import datetime
import tabulate
from collections import defaultdict
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.linear_model import LogisticRegression, SGDClassifier, Lasso, ElasticNet
from sklearn.naive_bayes import MultinomialNB, GaussianNB, BernoulliNB, ComplementNB
from sklearn.svm import LinearSVC, SVC
from sklearn.decomposition import TruncatedSVD

CLASSIFIERS = [
    SGDClassifier(loss='log'),
    # LogisticRegression(),
    # LinearSVC(),
    # SVC(),
    # BernoulliNB()
]


class TrainingPipeline(object):
    def __init__(self, classifier):
        self.MODEL_DIRECTORY = '/Users/mattdahl/Documents/nd/research/projects/scrutiny_scaling/models'
        self.corpus_loader = CorpusLoader(PickledCorpusReader(), 10, shuffle=True, categories=['CB', 'CN', 'RB'])
        self.classifier = classifier
        self.pipeline = self._build()
        self.scores = defaultdict(list)

    def _build(self):
        return Pipeline([
            ('normalize', OpinionNormalizer()),
            ('vectorize', TfidfVectorizer(
                tokenizer=lambda w: w,
                preprocessor=None,
                lowercase=False
            )),
            ('classify', self.classifier)
        ])

    def train(self):
        # k-fold cross-validation
        for X_train, X_test, y_train, y_test in self.corpus_loader:
            self.pipeline.fit(X_train, y_train)
            y_hat = self.pipeline.predict(X_test)

            self.scores['precision'].append(precision_score(y_test, y_hat, average='weighted'))
            self.scores['recall'].append(recall_score(y_test, y_hat, average='weighted'))
            self.scores['accuracy'].append(accuracy_score(y_test, y_hat))
            self.scores['f1'].append(f1_score(y_test, y_hat, average='weighted'))

    def get_scores(self):
        fields = ['model', 'precision', 'recall', 'accuracy', 'f1']
        table = []
        row = [str(self.classifier.__class__.__name__)]
        for field in fields[1:]:
            row.append(np.mean(self.scores[field]))
        table.append(row)

        return tabulate.tabulate(table, headers=fields)

    def save(self):
        file_name = self.classifier.__class__.__name__ + '-' + str(datetime.datetime.now().isoformat()) + '.pickle'
        file = open(os.path.join(self.MODEL_DIRECTORY, file_name), 'wb')
        pickle.dump(self.classifier, file)
        file.close()


for classifier in CLASSIFIERS:
    pipeline = TrainingPipeline(classifier)
    pipeline.train()
    pipeline.save()
    print(pipeline.get_scores())
