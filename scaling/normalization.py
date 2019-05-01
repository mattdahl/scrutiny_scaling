#!/usr/bin/env python3
import nltk
import unicodedata
import re

from corpus import PickledCorpusReader
from collections import Counter
from itertools import chain
from nltk.corpus import wordnet as wn
from nltk.stem.wordnet import WordNetLemmatizer
from sklearn.base import BaseEstimator, TransformerMixin


class OpinionNormalizer(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.LEMMATIZER = WordNetLemmatizer()
        self.STOPWORDS = self._load_stopwords()
        self.ROMAN_NUMERAL_REGEX = re.compile('^M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$', re.IGNORECASE)

    def _load_stopwords(self):
        stopwords = [
            nltk.corpus.stopwords.words('english'),
            self._load_case_factors_stopwords(),
            self._load_justices_stopwords()
        ]
        return list(set(chain.from_iterable(stopwords)))

    def _load_case_factors_stopwords(self):
        stopwords = []
        case_factors_stopwords = open('/Users/mattdahl/Documents/nd/research/projects/scrutiny_scaling/data/stopwords/case_factors.txt')
        for line in case_factors_stopwords.readlines():
            line = line.strip()
            if line and not line.startswith('#'):
                stopwords.append(line)

        return stopwords

    def _load_justices_stopwords(self):
        stopwords = []
        case_factors_stopwords = open('/Users/mattdahl/Documents/nd/research/projects/scrutiny_scaling/data/stopwords/justices.txt')
        for line in case_factors_stopwords.readlines():
            line = line.strip()
            if line:
                stopwords.extend(line.split())

        return stopwords

    def _is_punctuation(self, token):
        return all(
            unicodedata.category(char).startswith('P') for char in token
        )

    def _is_stopword(self, token):
        return token.lower() in self.STOPWORDS

    def _is_number(self, token):
        return token.isdigit() or any(char.isdigit() for char in token) or re.match(self.ROMAN_NUMERAL_REGEX, token)

    def _is_proper_noun(self, tag):
        return tag == 'NNP' or tag == 'NNPS'

    def _lemmatize(self, token, pos_tag):
        tag = {
            'N': wn.NOUN,
            'V': wn.VERB,
            'R': wn.ADV,
            'J': wn.ADJ
        }.get(pos_tag[0], wn.NOUN)

        return self.LEMMATIZER.lemmatize(token, tag)

    def _normalize(self, document):
        lemmatized = [
            self._lemmatize(token, tag).lower()
            for paragraph in document
            for sentence in paragraph
            for (token, tag) in sentence if not self._is_proper_noun(tag)
        ]
        filtered = [
            token for token in lemmatized
            if not self._is_punctuation(token) and not self._is_number(token) and not self._is_stopword(token)
        ]
        return filtered

    def fit(self, X, y=None):
        return self

    def transform(self, documents):
        for document in documents:
            yield self._normalize(document)
