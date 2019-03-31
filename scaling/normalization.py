#!/usr/bin/env python3
import nltk
import unicodedata

from nltk.corpus import wordnet as wn
from nltk.stem.wordnet import WordNetLemmatizer
from sklearn.base import BaseEstimator, TransformerMixin


class OpinionNormalizer(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.STOPWORDS = self._load_stopwords()
        self.LEMMATIZER = WordNetLemmatizer()

    def _load_stopwords(self):
        return set(nltk.corpus.stopwords.words('english'))

    def _is_punctuation(self, token):
        return all(
            unicodedata.category(char).startswith('P') for char in token
        )

    def _is_stopword(self, token):
        return token.lower() in self.STOPWORDS

    def _is_number(self, token):
        return token.isdigit()

    def _lemmatize(self, token, pos_tag):
        tag = {
            'N': wn.NOUN,
            'V': wn.VERB,
            'R': wn.ADV,
            'J': wn.ADJ
        }.get(pos_tag[0], wn.NOUN)

        return self.LEMMATIZER.lemmatize(token, tag)

    def _normalize(self, document):
        return [
            self._lemmatize(token, tag).lower()
            for paragraph in document
            for sentence in paragraph
            for (token, tag) in sentence
            if not self._is_punctuation(token) and not self._is_number(token) and not self._is_stopword(token)
        ]

    def fit(self, X, y=None):
        return self

    def transform(self, documents):
        for document in documents:
            yield self._normalize(document)
