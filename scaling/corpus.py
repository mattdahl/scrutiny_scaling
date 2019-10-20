#!/usr/bin/env python3
from settings import CORPUS_DIRECTORY_DEV, CORPUS_DIRECTORY_TRAIN

import os
import pickle
import numpy as np

from nltk.corpus.reader.api import CategorizedCorpusReader, CorpusReader
from sklearn.model_selection import KFold


# Reader that consumes the preprocessed, pickled version of the corpus
class PickledCorpusReader(CategorizedCorpusReader, CorpusReader):
    def __init__(self, dev=True):
        # File directories
        self.CORPUS_DIRECTORY = CORPUS_DIRECTORY_DEV if dev else CORPUS_DIRECTORY_TRAIN
        self.FILEIDS = [f for f in os.listdir(self.CORPUS_DIRECTORY) if not f.startswith('.')]

        # Terms
        self.TERMS = set()

        # Super classes
        CategorizedCorpusReader.__init__(self, {'cat_map': self._make_cat_map()})
        CorpusReader.__init__(self, root=self.CORPUS_DIRECTORY, fileids=self.FILEIDS)

    def _make_cat_map(self):
        category_map = {}
        for file_name in self.FILEIDS:
            if not file_name.startswith('.'):
                tokenized_file_name = file_name.split('-')
                speech_category = tokenized_file_name[0]
                term_category = tokenized_file_name[1]
                category_map[file_name] = [speech_category, term_category, speech_category + '-' + term_category]
                self.TERMS.add(int(term_category))
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

    # Overrides the fileids() method to accommodate term category filtering
    def fileids(self, categories=None):
        expanded_categories = []
        for category in categories:
            if category.startswith('>'):  # All speech categories, terms later than
                term = int(category[1:])
                expanded_categories += [str(i) for i in self.TERMS if i > term]
            elif category.startswith('<'):  # All speech categories, terms earlier than
                term = int(category[1:])
                expanded_categories += [str(i) for i in self.TERMS if i < term]
            elif len(category) > 2 and category[2] is '>':  # Specific speech category, terms later than
                speech_category = category[0:2]
                term = int(category[3:])
                expanded_categories += [speech_category + '-' + str(i) for i in self.TERMS if i > term]
            elif len(category) > 2 and category[2] is '<':  # Specific speech category, terms earlier than
                speech_category = category[0:2]
                term = int(category[3:])
                expanded_categories += [speech_category + '-' + str(i) for i in self.TERMS if i < term]
            else:  # Speech category
                expanded_categories += category

        return super().fileids(expanded_categories)

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
    def __init__(self, reader, folds=4, shuffle=True, categories=None):
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
