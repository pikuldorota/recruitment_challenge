import os
import argparse
import pandas as pd
import pycountry


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
        def warning(msg):
            print('WARNING: {}'.format(msg))
    else:
        def critical(msg):
            pass
        def warning(msg):
            pass

    if not os.path.isfile(args.input_file):
        critical("Input file doesn't exist: {}".format(args.input_file))
    try:
        data = pd.read_csv(args.input_file, names=['date', 'state name', 'impressions', 'CTR'])
    except UnicodeDecodeError:
        data = pd.read_csv(args.input_file, names=['date', 'state name', 'impressions', 'CTR'], encoding='utf-16')
    data['country code'] = data.apply(add_country_code, axis=1)
    grouped = data.groupby(['date', 'country code'])
    processed = map(process, grouped)
    output = pd.DataFrame(processed)
    output[0] = pd.to_datetime(output[0])
    output.sort_values([0, 1])

    if os.path.isfile(args.output_file) and os.path.getsize(args.output_file):
        critical("Output file exists and is not empty")
    if args.input_file == args.output_file:
        warning("Input and output file is the same file")
    output.to_csv(args.output_file, index=False, header=None, encoding="utf-8", line_terminator='\n')


# output_path to not empty file => warning
# wrong type of value in cell => warning about omitting
# strange number of columns in any row => warning
# some checking for headers
# errors to stderr - anything strange in file
# add requirements file
# accepts only csv with commas as seperator
# make verbose more verbose
# add logging to stderr