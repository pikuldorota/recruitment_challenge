import os
import sys
import argparse
import pycountry
import pandas as pd


def __read_file(input_file):
    if not os.path.isfile(input_file):
        critical("Input file doesn't exist: {}".format(input_file))
    try:
        file = pd.read_csv(input_file, names=['date', 'state name', 'impressions', 'CTR'])
    except UnicodeDecodeError:
        file = pd.read_csv(input_file, names=['date', 'state name', 'impressions', 'CTR'], encoding='utf-16')
    return file


def __filter_data(data):
    size = len(data.index)
    data = data[data.date.str.contains(r'^\d{2}\/\d{2}\/\d{4}$')]
    data = data[data.impressions.apply(lambda x: x.isnumeric())]
    data = data[data.CTR.str.contains(r'^\d+\.\d+%$')]
    if len(data) < size:
        if size - len(data) == 1:
            warning('1 row was removed during filtering')
        else:
            warning("{} rows were removed during filtering".format(size - len(data)))


def __add_country_code(row):
    try:
        code = pycountry.subdivisions.lookup(row['state name']).country_code
        country_code = pycountry.countries.lookup(code).alpha_3
    except LookupError:
        warning('State {} not found'.format(row['state name']))
        country_code = 'XXX'
    return country_code


def __process(group):
    date = group[0][0]
    country_code = group[0][1]
    impressions = group[1]['impressions'].sum()
    clicks = round((group[1]['CTR'].str.rstrip('%').astype(float)/100.0*float(group[1]['impressions'])).sum())
    return [date, country_code, impressions, clicks]


def __save_data(output_file, input_file):
    if os.path.isfile(output_file) and os.path.getsize(output_file):
        critical("Output file exists and is not empty")
    if input_file == output_file:
        warning("Input and output file is the same file")
    output.to_csv(output_file, index=False, header=None, encoding="utf-8", line_terminator='\n')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process CSV file to AdTech platform format')
    parser.add_argument('input_file', help='path to CSV file for processing', nargs='?', default='../data/example.csv')
    parser.add_argument('output_file', help='path to place where result will be saved', nargs='?',
                        default='../data/result.csv')
    parser.add_argument('-v', '--verbose', action='store_true', help='increase output verbosity')
    args = parser.parse_args()

    def critical(msg):
        if args.verbose:
            print('CRITICAL: {}'.format(msg))
        sys.exit('CRITICAL: {}'.format(msg))

    def warning(msg):
        if args.verbose:
            print('WARNING: {}'.format(msg))
        print('WARNING: {}'.format(msg), file=sys.stderr)

    def info(msg):
        if args.verbose:
            print('INFO: {}'.format(msg))


    info('read file')
    data = __read_file(args.input_file)

    info('filter data')
    __filter_data(data)

    info('find country codes')
    data['country code'] = data.apply(__add_country_code, axis=1)

    info('group data')
    grouped = data.groupby(['date', 'country code'])

    info('process grouped data')
    processed = map(__process, grouped)
    output = pd.DataFrame(processed)
    output[0] = pd.to_datetime(output[0])

    info('sort data')
    output.sort_values([0, 1])

    info('save data')
    __save_data(args.output_file, args.input_file)
