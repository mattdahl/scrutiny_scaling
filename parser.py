# -*- coding: utf-8 -*-
import os
import sys
import re

RAW_DIRECTORY = 'data/corpus/raw/'
PARSED_DIRECTORY = 'data/corpus/parsed/'
FILE_NAME_REGEX = re.compile(r'(.+)(?=(\d{3}) U\.S\. (\d+)(\.txt))')
WHITELIST = [
    "Swanner v. Anchorage Equal Rights Comm'n, 513 U.S. 979.txt"  # This case is a simple denial of cert and contains no majority opinion
]

def build_majority_opinion_regex():
    # Regex explanation:
    # `beginning` is a list of strings that form alternative positive lookbehinds (beginning of the majority opinion)
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
    return begin_concatenated + r'(.*?)' + end_concatenated


def extract_majority_opinion(opinion_text, file_name):
    majority_opinion = re.search(build_majority_opinion_regex(), opinion_text, flags=re.DOTALL)
    if majority_opinion is None:
        if file_name in WHITELIST:
            return ''
        else:
            print opinion_text
            sys.exit('Error! No opinion found.')
    else:
        return majority_opinion.group() # Take the first (only) extracted opinion


def rewrite_file_name(file_directory, file_name):
    match = re.match(FILE_NAME_REGEX, file_name)

    category = file_directory.upper()
    citation = match.group(2) + '|' + match.group(3)
    case_name = match.group(1)[:-2].replace(' ', '_')
    extension = match.group(4)

    return '-'.join([category, citation, case_name, extension])


def parse():
    file_directories = [d for d in os.listdir(RAW_DIRECTORY) if not d.startswith('.')]

    for fd in file_directories:
        sub_directory = os.path.join(RAW_DIRECTORY, fd)
        files = [f for f in os.listdir(sub_directory) if not f.startswith('.')]

        for f in files:
            file_content = open(os.path.join(os.getcwd(), sub_directory, f), 'r').read()

            # Get parsed file name and content
            new_file_name = rewrite_file_name(fd, f)
            new_file_content = extract_majority_opinion(file_content, f)

            # Save parsed file to disk
            new_file = open(os.path.join(os.getcwd(), PARSED_DIRECTORY, new_file_name), 'w')
            new_file.write(new_file_content)
            new_file.close()

parse()
