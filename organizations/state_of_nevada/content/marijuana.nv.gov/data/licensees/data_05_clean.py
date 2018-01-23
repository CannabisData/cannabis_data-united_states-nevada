"""Script to clean and organize Nevada licensee data."""

import os
import sys
import csv
import json

CULTIVATOR = 'cultivator'
PRODUCER = 'producer'
DISTRIBUTOR = 'distributor'
DISPENSARY = 'dispensary'
LAB = 'lab'

SOURCE_DIRECTORY = 'nevada-licensees-00-source/nevada-licensees.csv'
SOURCE_FILENAME = {
    CULTIVATOR: 'Cultivation-Table 1.csv',
    PRODUCER: 'Production-Table 1.csv',
    DISTRIBUTOR: 'MME Dist-Table 1.csv',
    DISPENSARY: 'Dispensary-Table 1.csv',
    LAB: 'Lab-Table 1.csv'
}

TARGET_FILENAME = 'nevada-licensees-05-clean.json'


def main():
    """Main program."""
    licensees = []

    if not os.path.isdir(SOURCE_DIRECTORY):
        sys.exit('Source directory unavailable: {}'.format(SOURCE_DIRECTORY))

    for key, source_filename in SOURCE_FILENAME.items():
        source_path = SOURCE_DIRECTORY + '/' + source_filename
        print('Source path: {}'.format(source_path))
        path_exists = os.path.exists(source_path)

        if not path_exists:
            print('- Skipping')
            continue

        print('+ Reading...')
        with open(source_path, mode='r') as infile:
            reader = csv.DictReader(infile)
            try:
                for row in reader:
                    row['type'] = key
                    licensees.append(row)
                    # print(row)
            except csv.Error as error:
                sys.exit('line {}: {}'.format(reader.line_num, error))

    total_licensees = len(licensees)
    print('Total licensee records: {}'.format(total_licensees))

    print('Processing licensees...')

    print('* Removing empty field due to trailing separator...')
    fields_to_remove = ['']
    for licensee in licensees:
        for key in fields_to_remove:
            del licensee[key]

    print('* Stripping leading and trailing whitespace from all values...')
    for licensee in licensees:
        for key, value in licensee.items():
            licensee[key] = value.strip()

    print('Writing output to {}'.format(TARGET_FILENAME))
    with open(TARGET_FILENAME, 'w') as outfile:
        json.dump(licensees, outfile, sort_keys=True, indent=2,
                  separators=(',', ': '))


main()
