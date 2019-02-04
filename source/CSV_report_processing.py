import os
import sys
import argparse
import pycountry
import pandas as pd


def read_file(input_file):
    if not os.path.isfile(input_file):
        critical("Input file doesn't exist: {}".format(input_file))
    try:
        file = pd.read_csv(input_file, names=['date', 'state name', 'impressions', 'CTR'])
    except UnicodeDecodeError:
        file = pd.read_csv(input_file, names=['date', 'state name', 'impressions', 'CTR'], encoding='utf-16')
    return file


def add_country_code(row):
    try:
        code = pycountry.subdivisions.lookup(row['state name']).country_code
        country_code = pycountry.countries.lookup(code).alpha_3
    except LookupError:
        warning('State {} not found'.format(row['state name']))
        country_code = 'XXX'
    return country_code


def process(group):
    date = group[0][0]
    country_code = group[0][1]
    impressions = group[1]['impressions'].sum()
    clicks = round((group[1]['CTR'].str.rstrip('%').astype(float)/100.0*group[1]['impressions']).sum())
    return [date, country_code, impressions, clicks]


def save_data(output_file, input_file):
    if os.path.isfile(output_file) and os.path.getsize(output_file):
        critical("Output file exists and is not empty")
    if input_file == output_file:
        warning("Input and output file is the same file")
    output.to_csv(output_file, index=False, header=None, encoding="utf-8", line_terminator='\n')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process CSV file to AdTech platform format')
    parser.add_argument('input_file', help='path to CSV file for processing', nargs='?', default='../data/utf16.csv')
    parser.add_argument('output_file', help='path to place where result will be saved', nargs='?',
                        default='../data/result.csv')
    parser.add_argument('-v', '--verbose', action='store_true', help='increase output verbosity')
    args = parser.parse_args()

    if args.verbose:
        def critical(msg):
            print('CRITICAL: {}'.format(msg))
            print('CRITICAL: {}'.format(msg), file=sys.stderr)

        def warning(msg):
            print('WARNING: {}'.format(msg))
            print('WARNING: {}'.format(msg), file=sys.stderr)

        def info(msg):
            print('INFO: {}'.format(msg))

    else:
        def critical(msg):
            print('CRITICAL: {}'.format(msg), file=sys.stderr)

        def warning(msg):
            print('WARNING: {}'.format(msg), file=sys.stderr)

        def info(_):
            """With verbosity off information won't be shown anywhere"""
            pass

    info('read file')
    data = read_file(args.input_file)

    info('find country codes')
    data['country code'] = data.apply(add_country_code, axis=1)

    info('group data')
    grouped = data.groupby(['date', 'country code'])

    info('process grouped data')
    processed = map(process, grouped)
    output = pd.DataFrame(processed)
    output[0] = pd.to_datetime(output[0])

    info('sort data')
    output.sort_values([0, 1])

    info('save data')
    save_data(args.output_file, args.input_file)
