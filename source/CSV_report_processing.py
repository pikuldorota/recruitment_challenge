import os
import sys
import argparse
import pycountry
import pandas as pd


def __read_file(input_file):
    """Reads csv file to pandas DataFrame and gives the columns names: data, state name, impressions and CTR"""
    if not os.path.isfile(input_file):
        critical("Input file doesn't exist: {}".format(input_file))
    try:
        file = pd.read_csv(input_file, names=['date', 'state name', 'impressions', 'CTR'])
    except UnicodeDecodeError:
        file = pd.read_csv(input_file, names=['date', 'state name', 'impressions', 'CTR'], encoding='utf-16')
    return file


def __filter_data(data_frame):
    """
    Filters rows to get only this with correct values according to specification
    date: format should be dd/mm/yyyy
    impressions: it should be number
    CTR: it should be number followed by '%' sign
    """
    size = len(data_frame.index)
    data_frame = data_frame[data_frame.date.str.contains(r'^\d{2}\/\d{2}\/\d{4}$')]

    def __check_if_int(x):
        """This function checks if given x can be interpreted as non-negative int object"""
        try:
            if int(x) >= 0 :
                return True
            else:
                return False
        except (ValueError, TypeError):
            return False

    data_frame = data_frame[data_frame.impressions.apply(lambda x: __check_if_int(x))]
    data_frame = data_frame[data_frame.CTR.str.contains(r'^\d+\.\d+%$')]
    if len(data_frame) < size:
        if size - len(data_frame) == 1:
            warning('1 row was removed during filtering')
        else:
            warning("{} rows were removed during filtering".format(size - len(data_frame)))
    return data_frame


def __add_country_code(row):
    """Adds to row it's country code according to state name. If state name doesn't have code then set it to 'XXX'"""
    try:
        code = pycountry.subdivisions.lookup(row['state name']).country_code
        country_code = pycountry.countries.lookup(code).alpha_3
    except LookupError:
        warning('State {} not found'.format(row['state name']))
        country_code = 'XXX'
    return country_code


def __process(group):
    """
    Given group of rows having the same date and country code produce data for row including sum of impressions
    and number of clicks calculated from impressions and CTR values
    """
    date = group[0][0]
    country_code = group[0][1]
    impressions = group[1]['impressions'].sum()
    # Line below sums clicks counted as CTR*impressions
    clicks = round(
        (group[1]['CTR'].str.rstrip('%').astype(float) / 100.0 * (group[1]['impressions']).astype(float)).sum())
    return [date, country_code, impressions, clicks]


def __save_data(output_file, input_file):
    """Saves calculated data to given file."""
    if input_file == output_file:
        warning("Input and output file is the same file")
    elif os.path.isfile(output_file) and os.path.getsize(output_file):
        critical("Output file exists and is not empty")
    output.to_csv(output_file, index=False, header=None, encoding="utf-8", line_terminator='\n')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process CSV file to AdTech platform format')
    parser.add_argument('input_file', help='path to CSV file for processing', nargs='?', default='../data/example.csv')
    parser.add_argument('output_file', help='path to place where result will be saved', nargs='?',
                        default='../data/result.csv')
    parser.add_argument('-v', '--verbose', action='store_true', help='increase output verbosity')
    args = parser.parse_args()

    def critical(msg):
        """Prints error message and exits program"""
        if args.verbose:
            print('CRITICAL: {}'.format(msg))
        sys.exit('CRITICAL: {}'.format(msg))

    def warning(msg):
        """Prints non-critical error and continue"""
        if args.verbose:
            print('WARNING: {}'.format(msg))
        print('WARNING: {}'.format(msg), file=sys.stderr)

    def info(msg):
        """Prints information for verbose output"""
        if args.verbose:
            print('INFO: {}'.format(msg))


    info('read file')
    data = __read_file(args.input_file)

    info('filter data')
    data = __filter_data(data)

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
