import os
import sys
import re

RAW_DIRECTORY = 'data/corpus/raw/'
PARSED_DIRECTORY = 'data/corpus/parsed/'

FILE_NAME_REGEX = re.compile(r'(.+)(?=(\d{3}) U\.S\. (\d+)(\.txt))')

file_directories = [d for d in os.listdir(RAW_DIRECTORY) if not d.startswith('.')]

for fd in file_directories:
    sub_directory = os.path.join(RAW_DIRECTORY, fd)
    file_names = [f for f in os.listdir(sub_directory) if not f.startswith('.')]

    for fn in file_names:
        match = re.match(FILE_NAME_REGEX, fn)

        # Build new file name
        category = fd.upper()
        citation = match.group(2) + '|' + match.group(3)
        case_name = match.group(1)[:-2].replace(' ', '_')
        extension = match.group(4)
        new_file_name = '-'.join([category, citation, case_name, extension])

        # Save new file to disk
        new_file = open(os.path.join(os.getcwd(), PARSED_DIRECTORY, new_file_name), 'w')
        old_file_content = open(os.path.join(os.getcwd(), sub_directory, fn), 'r').read()
        new_file.write(old_file_content)
        new_file.close()
