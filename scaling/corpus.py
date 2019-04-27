#!/usr/bin/env python3
import os
import pickle
import numpy as np

from nltk.corpus.reader.api import CategorizedCorpusReader, CorpusReader
from sklearn.model_selection import KFold


# Reader that consumes the preprocessed, pickled version of the corpus
class PickledCorpusReader(CategorizedCorpusReader, CorpusReader):
    def __init__(self, dev=False):
        # File directories
        self.CORPUS_DIRECTORY = 'data/corpus/preprocessed/dev/' if dev else 'data/corpus/preprocessed/train/'
        self.FILEIDS = [f for f in os.listdir(self.CORPUS_DIRECTORY) if not f.startswith('.')]

        # Super classes
        CategorizedCorpusReader.__init__(self, {'cat_map': self._make_cat_map()})
        CorpusReader.__init__(self, root=self.CORPUS_DIRECTORY, fileids=self.FILEIDS)

    def _make_cat_map(self):
        category_map = {}
        for file_name in self.FILEIDS:
            if not file_name.startswith('.'):
                tokenized_file_name = file_name.split('-')
                category = tokenized_file_name[0]
                category_map[file_name] = [category]
        return category_map

    # Returns a list of fileids or categories depending on what is passed
    def _resolve(self, fileids, categories):
        # If both fileids and categories are passed, throw an error
        if fileids and categories:
            raise ValueError('Specify fileids or categories, not both.')

        # If categories are passed, get the fileids for those categories
        elif categories:
            return self.fileids(categories)

        # If fileids are passed, just return those
        elif fileids:
            return fileids

    def docs(self, fileids=None, categories=None):
        fileids = self._resolve(fileids, categories)
        for path, enc, fileid in self.abspaths(fileids, True, True):
            with open(path, 'rb') as f:
                yield pickle.load(f)

    def paras(self, fileids=None, categories=None):
        for doc in self.docs(fileids=fileids, categories=categories):
            for paragraph in doc:
                yield paragraph

    def sents(self, fileids=None, categories=None):
        for paragraph in self.paras(fileids=fileids, categories=categories):
            for sentence in paragraph:
                yield sentence

    def tokens(self, fileids=None, categories=None):
        for sentence in self.sents(fileids=fileids, categories=categories):
            for token in sentence:
                yield token

    def words(self, fileids=None, categories=None):
        for token in self.tokens(fileids=fileids, categories=categories):
            yield token[0]

    def tags(self, fileids=None, categories=None):
        for token in self.tokens(fileids=fileids, categories=categories):
            yield token[1]


# Loader that serves a folded version of the corpus
class CorpusLoader(object):
    def __init__(self, reader, folds=3, shuffle=True, categories=None):
        self.reader = reader
        self.folds = None if folds == 1 else KFold(n_splits=folds, shuffle=shuffle)
        self.files = np.asarray(self.reader.fileids(categories=categories))

    def fileids(self, index=None):
        if index is None:
            return self.files

        return self.files[index]

    def documents(self, index=None):
        return self.reader.docs(fileids=[fileid for fileid in self.fileids(index)])

    def labels(self, index=None):
        labels = []

        fileids = self.fileids(index)
        for fileid in fileids:
            labels.append(self.reader.categories(fileids=[fileid])[0])

        return labels

    def __iter__(self):
        for train_index, test_index in self.folds.split(self.files):
            X_train = self.documents(train_index)
            y_train = self.labels(train_index)

            X_test = self.documents(test_index)
            y_test = self.labels(test_index)

            yield (X_train, X_test, y_train, y_test)
