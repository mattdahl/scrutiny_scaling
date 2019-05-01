#!/usr/bin/env python3
from normalization import OpinionNormalizer, ToArray
from corpus import PickledCorpusReader, CorpusLoader

import os
import time
import tabulate
import dill as pickle
from collections import defaultdict
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, r2_score, explained_variance_score, mean_squared_error
from sklearn.linear_model import LogisticRegression, SGDClassifier, Lasso, ElasticNet, Ridge
from sklearn.naive_bayes import MultinomialNB, GaussianNB, BernoulliNB, ComplementNB
from sklearn.svm import LinearSVC, SVC, SVR
from sklearn.decomposition import TruncatedSVD, PCA


class ModelTrainer(object):
    def __init__(self):
        self.MODEL_DIRECTORY = '/Users/mattdahl/Documents/nd/research/projects/scrutiny_scaling/scaling/models'
        self.categories = ['LP', 'CN', 'CB']
        self.corpus_reader = PickledCorpusReader(dev=False)
        self.corpus_loader = CorpusLoader(self.corpus_reader, 8, shuffle=True, categories=self.categories)
        self.pipelines = self._build_pipelines()

    def _build_pipelines(self):
        pipelines = []

        for classifier in self.classifiers:
            pipeline = Pipeline([
                ('normalize', OpinionNormalizer()),
                ('vectorize', TfidfVectorizer(
                    tokenizer=lambda w: w,
                    preprocessor=None,
                    lowercase=False
                )),
                #('to_array', ToArray()),
                #('reduce', TruncatedSVD(n_components=1000)),
                ('classify', classifier)
            ])
            pipelines.append(pipeline)

        return pipelines

    def save(self):
        for pipeline in self.pipelines:
            file_name = pipeline.named_steps['classify'].__class__.__name__ + '-' + str(time.time()) + '.pickle'
            file = open(os.path.join(self.MODEL_DIRECTORY, file_name), 'wb')
            pickle.dump(pipeline, file)
            file.close()


class ClassificationModelTrainer(ModelTrainer):
    def __init__(self):
        self.classifiers = [
            #SGDClassifier(loss='log'),
            #SVR(kernel='linear'),
            LogisticRegression(),
            LogisticRegression(
                multi_class='multinomial',
                solver='newton-cg',
                fit_intercept=True
            )
        ]
        super().__init__()

    def train(self):
        for pipeline in self.pipelines:
            X_train = self.corpus_reader.docs(categories=self.categories)
            y_train = [self.corpus_reader.categories(fileids=[fileid])[0] for fileid in self.corpus_reader.fileids(categories=self.categories)]
            pipeline.fit(X_train, y_train)

    def validate(self):
        fields = ['model', 'precision', 'recall', 'accuracy', 'f1']
        table = []

        for pipeline in self.pipelines:
            scores = defaultdict(list)

            # Uses k-fold cross-validation
            for X_train, X_test, y_train, y_test in self.corpus_loader:
                pipeline.fit(X_train, y_train)
                y_hat = pipeline.predict(X_test)

                scores['precision'].append(precision_score(y_test, y_hat, average='weighted'))
                scores['recall'].append(recall_score(y_test, y_hat, average='weighted'))
                scores['accuracy'].append(accuracy_score(y_test, y_hat))
                scores['f1'].append(f1_score(y_test, y_hat, average='weighted'))

            row = [str(pipeline.named_steps['classify'].__class__.__name__)]
            for field in fields[1:]:
                row.append(np.mean(scores[field]))
            table.append(row)

        table.sort(key=lambda row: row[-1], reverse=True)
        return tabulate.tabulate(table, headers=fields)


class RegressionModelTrainer(ModelTrainer):
    def __init__(self):
        self.classifiers = [
            Ridge(alpha=0.5),
            #Lasso(alpha=0.1),
        ]
        super().__init__()

    def _map_scores(self, categories):
        score_map = {
            'LP': 1,
            'CN': 2,
            'CB': 3
        }
        return [score_map[category] for category in categories]

    def train(self):
        for pipeline in self.pipelines:
            X_train = self.corpus_reader.docs(categories=self.categories)
            y_train = self._map_scores([self.corpus_reader.categories(fileids=[fileid])[0] for fileid in self.corpus_reader.fileids(categories=self.categories)])
            pipeline.fit(X_train, y_train)

    def validate(self):
        fields = ['model', 'r2', 'v', 'mse']
        table = []

        for pipeline in self.pipelines:
            scores = defaultdict(list)

            # Uses k-fold cross-validation
            for X_train, X_test, y_train, y_test in self.corpus_loader:
                y_train = self._map_scores(y_train)
                y_test = self._map_scores(y_test)

                pipeline.fit(X_train, y_train)
                y_hat = pipeline.predict(X_test)

                scores['r2'].append(r2_score(y_test, y_hat))
                scores['v'].append(explained_variance_score(y_test, y_hat))
                scores['mse'].append(mean_squared_error(y_test, y_hat))

            row = [str(pipeline.named_steps['classify'].__class__.__name__)]
            for field in fields[1:]:
                row.append(np.mean(scores[field]))
            table.append(row)

        table.sort(key=lambda row: row[-1], reverse=True)
        return tabulate.tabulate(table, headers=fields)
