#!/usr/bin/env python3
import os
import pickle
import re
import sys

from nltk import pos_tag, sent_tokenize, wordpunct_tokenize


# Takes raw LexisNexis .txt files; tokenizes them into paragraphs, sentences,
# and words; tags them with part of speech tags; and saves them in a pickled
# format for future consumption.
class Preprocessor(object):
    def __init__(self):
        # File directories
        self.RAW_DIRECTORY = '/Users/mattdahl/Documents/nd/research/projects/scrutiny_scaling/data/corpus/raw'
        self.PROCESSED_DIRECTORY = '/Users/mattdahl/Documents/nd/research/projects/scrutiny_scaling/data/corpus/preprocessed'

        # Regexes
        self.FILE_NAME_REGEX = re.compile(r'(.+)(?=(\d{3}) U\.S\. (\d+)(\.txt))')
        self.MAJORITY_OPINION_REGEX = self._build_majority_opinion_regex()

        # Whitelist of documents to skip
        self.WHITELIST = [
            "Swanner v. Anchorage Equal Rights Comm'n, 513 U.S. 979.txt"  # This case is a simple denial of cert and contains no majority opinion
        ]

    # Main executable method
    def process(self):
        file_directories = [d for d in os.listdir(self.RAW_DIRECTORY) if not d.startswith('.')]

        for fd in file_directories:
            sub_directory = os.path.join(self.RAW_DIRECTORY, fd)
            file_names = [f for f in os.listdir(sub_directory) if not f.startswith('.')]

            for f in file_names:
                if f not in self.WHITELIST:
                    # Read document
                    file_content = open(os.path.join(sub_directory, f), 'r').read()

                    # Process document
                    try:
                        majority_opinion = self._extract_majority_opinion(opinion_text=file_content)
                    except LookupError:
                        sys.exit('Error! No opinion found in file {}.'.format(f))
                    processed_opinion = list(self._tokenize_and_tag(text=majority_opinion))
                    new_file_name = self._rewrite_file_name(file_directory=fd, file_name=f)

                    # Save processed document to disk
                    new_file = open(os.path.join(os.getcwd(), self.PROCESSED_DIRECTORY, new_file_name), 'wb')
                    pickle.dump(processed_opinion, new_file, pickle.HIGHEST_PROTOCOL)
                    new_file.close()
                    print('Wrote {}...'.format(new_file_name))

    def _tokenize_and_tag(self, text):
        for paragraph in text.splitlines():
            yield [
                pos_tag(wordpunct_tokenize(sentence))
                for sentence in sent_tokenize(paragraph)
            ]

    def _rewrite_file_name(self, file_directory, file_name):
        match = re.match(self.FILE_NAME_REGEX, file_name)

        category = file_directory.upper()
        citation = match.group(2) + '|' + match.group(3)
        case_name = match.group(1)[:-2].replace(' ', '_')
        extension = '.pickle'

        return '-'.join([category, citation, case_name]) + extension

    def _extract_majority_opinion(self, opinion_text):
        majority_opinion = re.search(self.MAJORITY_OPINION_REGEX, opinion_text)
        if majority_opinion is None:
            raise LookupError
        else:
            return majority_opinion.group()  # Take the first (only) extracted opinion

    def _build_majority_opinion_regex(self):
        # Regex explanation:
        # `begin` is a list of strings that form alternative positive lookbehinds (beginning of the majority opinion)
        # (.*?) is a lazy capturing group (the opinion)
        # `end` is a list of strings that form alternative positive lookaheads (end of majority opinion)
        begin = [
            r'Opinion by:',
            r'PER CURIAM'
        ]
        end = [
            r'End of Document',
            r'Dissent by:',
            r'Concur by:'
        ]

        begin_concatenated = r'(?:' + r'|'.join([r'(?<=' + re.escape(s) + r')' for s in begin]) + r')'
        end_concatenated = r'(?=' + r'|'.join([re.escape(s) for s in end]) + r')'

        # Build the regex string
        return re.compile(begin_concatenated + r'(.*?)' + end_concatenated, flags=re.DOTALL)
