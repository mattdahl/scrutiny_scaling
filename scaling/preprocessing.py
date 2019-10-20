#!/usr/bin/env python3
from settings import SCDB_DATA_FILE, CORPUS_DIRECTORY_RAW, CORPUS_DIRECTORY_DEV, CORPUS_DIRECTORY_TRAIN

import os
import pickle
import re
import sys
import csv

from nltk import pos_tag, sent_tokenize, wordpunct_tokenize
import pandas as pd


# Takes raw LexisNexis .txt files; extracts the majority opinion from each
# document; tokenizes it into paragraphs, sentences, and words; tags each word
# with its part of speech tag; and saves it in a pickled format for future
# consumption.
class Preprocessor(object):
    def __init__(self):
        # File directories
        self.RAW_DIRECTORY = CORPUS_DIRECTORY_RAW

        # SCDB Data
        self.SCDB_DATA = pd.read_csv(SCDB_DATA_FILE, encoding='Windows-1252')

        # Regexes
        self.FILE_NAME_REGEX = re.compile(r'(.+)(?=(\d{3}) U\.S\. (\d+)(?P<part>\(\d+\))?(\.txt))')
        self.MAJORITY_OPINION_REGEX = self._build_majority_opinion_regex()

        # Blacklist of documents to skip
        self.BLACKLIST = [
            'Swanner v. Anchorage Equal Rights Comm\'n, 513 U.S. 979.txt',  # Denial of cert
            'McConnell v. FEC, 540 U.S. 93(3).txt',  # This opinion concurs in the judgment but is really a dissent
            'Fair Drain Taxation, Inc. v. St. Clair Shores, 375 U.S. 258.txt',  # Empty per curiam decision
            'Fields v. Fairfield, 375 U.S. 248.txt',  # Empty per curiam decision
            'Grumman v. United States, 370 U.S. 288.txt',  # Empty per curiam decision
            'Kansas City Southern R. Co. v. Reily, 370 U.S. 289.txt',  # Empty per curiam decision
            'Macon v. Indiana, 375 U.S. 258.txt',  # Empty per curiam decision
            'McAllister v. Louisiana, 375 U.S. 260.txt',  # Empty per curiam decision
            'Milutin v. Bouchard, 370 U.S. 292.txt',  # Empty per curiam decision
            'Seelig v. United States, 370 U.S. 293.txt',  # Empty per curiam decision
            'Smith v. California, 375 U.S. 259.txt',  # Empty per curiam decision
            'Valenzuela v. Eyman, 370 U.S. 290.txt',  # Empty per curiam decision
            'Abernathy v. Alabama, 380 U.S. 447.txt',  # Empty per curiam decision
            'Atwood\'s Transport Lines, Inc. v. United States, 373 U.S. 377.txt',  # Empty per curiam decision
            'Avent v. North Carolina, 373 U.S. 375.txt',  # Empty per curiam decision
            'Baltimore & O. R. Co. v. Boston & M. R. Co., 373 U.S. 372.txt',  # Empty per curiam decision
            'Beard v. Dunbar, 373 U.S. 907.txt',   # Denial of writ of habeus corpus
            'Chicago & N. W. R. Co. v. Chicago, M. St. P. & P. R. Co., 380 U.S. 448.txt',  # Empty per curiam decision
            'Drexel v. Ohio Pardon & Parole Com., 373 U.S. 377.txt',  # Empty per curiam decision
            'Flora Constr. Co. v. Fireman\'s Fund Ins. Co., 373 U.S. 919.txt',  # Denial of rehearing
            'Gober v. Birmingham, 373 U.S. 374.txt',  # Empty per curiam decision
            'Illinois v. United States, 373 U.S. 378.txt',  # Empty per curiam decision
            'In re Simmons, 380 U.S. 960.txt',  # Empty motion
            'Keene v. Supreme Court of Alabama, 373 U.S. 907.txt',  # Denial of writ of mandamus
            'McKinnie v. Tennessee, 380 U.S. 449.txt',  # Empty per curiam decision
            'Page v. Green, 373 U.S. 907.txt',  # Denial of cert
            'Richards v. Pennsylvania, 373 U.S. 376.txt',  # Empty per curiam decision
            'Ship-By-Truck Co. v. United States, 373 U.S. 376.txt',  # Empty per curiam decision
            'Toffenetti Restaurant Co. v. NLRB, 373 U.S. 919.txt',  # Denial of rehearing
            'U. S. A. C. Transport, Inc. v. United States, 380 U.S. 450.txt',  # Empty per curiam decision
            'Int\'l Soc\'y for Krishna Consciousness v. Lee, 505 U.S. 672.txt',  # Concurrence erroneously marked as a majority opinion
            'Lee v. International Soc\'y for Krishna Consciousness, 505 U.S. 830.txt',  # Empty per curiam decision
        ]

        # Clean up some file names (LexisNexis cuts off after 100 characters)
        try:
            os.rename(os.path.join(self.RAW_DIRECTORY, 'cb', 'American Committee for Protection of Foreign Born v. Subversive Activities Control Board, 380 U.S. 5.txt'), os.path.join(self.RAW_DIRECTORY, 'cb', 'American Committee for Protection of Foreign Born v. Subversive Activities Control Board, 380 U.S. 503.txt'))
        except FileNotFoundError:
            pass

    # Main executable method
    def process(self, split=False):
        file_directories = [d for d in os.listdir(self.RAW_DIRECTORY) if not d.startswith('.')]

        for file_directory in file_directories:
            sub_directory = os.path.join(self.RAW_DIRECTORY, file_directory)
            file_names = [f for f in os.listdir(sub_directory) if not f.startswith('.')]

            for i, file_name in enumerate(file_names):
                if file_name not in self.BLACKLIST:
                    # Update status
                    print('Reading {}... '.format(file_name), end='')

                    # Read document
                    file_content = open(os.path.join(sub_directory, file_name), 'r').read()

                    # Process document
                    try:
                        majority_opinion = self._extract_majority_opinion(file_content)
                    except LookupError:
                        sys.exit('Error! No opinion found in file {}.'.format(file_name))
                    processed_opinion = list(self._tokenize_and_tag(majority_opinion))
                    new_file_name = self._rewrite_file_name(file_directory, file_name)

                    # Save processed document to disk
                    if split:
                        new_directory = CORPUS_DIRECTORY_DEV if i % 2 else CORPUS_DIRECTORY_TRAIN
                    else:
                        new_directory = CORPUS_DIRECTORY_DEV
                    new_file = open(os.path.join(new_directory, new_file_name), 'wb')
                    pickle.dump(processed_opinion, new_file, pickle.HIGHEST_PROTOCOL)
                    new_file.close()

                    # Update status
                    print('Success! Wrote: {}'.format(new_file_name))

    def _tokenize_and_tag(self, text):
        for paragraph in text.splitlines():
            yield [
                pos_tag(wordpunct_tokenize(sentence))
                for sentence in sent_tokenize(paragraph)
            ]

    def _get_term(self, reporter, page):
        citation_string = reporter + ' U.S. ' + page

        try:
            term = self.SCDB_DATA[self.SCDB_DATA.usCite == citation_string]['term'].item()
            return str(term)
        except:
            sys.exit('Error! No term found for citation {}.'.format(citation_string))

    def _rewrite_file_name(self, file_directory, file_name):
        match = re.match(self.FILE_NAME_REGEX, file_name)

        category = file_directory.upper()
        reporter = match.group(2)
        page = match.group(3)
        term = self._get_term(reporter, page)
        citation = reporter + '|' + page
        case_name = match.group(1)[:-2].replace(' ', '_')
        if match.group('part'):
            case_name += '_' + match.group('part')
        extension = '.pickle'

        return '-'.join([category, term, citation, case_name]) + extension

    def _extract_majority_opinion(self, opinion_text):
        majority_opinion = re.search(self.MAJORITY_OPINION_REGEX, opinion_text)
        if majority_opinion is None:
            raise LookupError
        else:
            majority_opinion = majority_opinion.group()
            majority_opinion = '\n'.join(majority_opinion.split('\n')[7:])  # Remove opinion header
            return majority_opinion

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
