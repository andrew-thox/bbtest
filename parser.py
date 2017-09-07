import csv
import os
import re
import json


CSV_DIR = os.path.dirname(os.path.realpath(__file__)) + '/static/'

csv_file_names = ['1.csv', '2.csv', '3.csv']

days = ['mon', 'tue', 'wed', 'thu', 'fri']

range_regex = re.compile('^((?:sun|mon|tue|wed|thu|fri|sat)(?:-)(?:sun|mon|tue|wed|thu|fri|sat)){1,7}')


def action(day, value):
    """Performs the correct math operation depending on day of the week
    Args:
        day: (str) mon, tue, wed... Used to determine whether number should be squared or multiplied
        value: (str) The value on which to perform the operation. Can also be an integer, just the csv parser return a
         string.
    Returns:
        (dict): with key action (square, or double) and result
        {'double': 6)
    NOTE: In retrospect probably would have done {'action': 'square', 'result', 6} and then manipulated that in the
        output. Instead of doing list(result.values())[0] below.
        """

    if day in ['mon', 'tue', 'wed']:
        return {'square': int(value) ** 2}
    elif day in ['thu', 'fri']:
        return {'double': int(value) * 2}


def expand_range(key, value):
    """Takes a key, value pair where key is a range and turns it into a dictionary where each day is a key
    Args:
        key: (str) the range key. For example: 'mon-thu'
        value: the value associated with range (in this case it's a integer represented as a str, but theoretically
            could be many things
    Returns:
        (dict) a dictionary where each day in the range has been expanded to its own key:
        {'mon': 2, 'tue': 2, 'wed': 2, 'thu': 2}
        """
    split = key.split('-')
    start = days.index(split[0])
    end = days.index(split[1])
    i = start
    expanded_range = {}
    while i <= end:
        expanded_range[days[i]] = value
        i += 1
    return expanded_range


def parse_csv(full_path):
    """Takes a path, opens files a csv, and returns a dictionary of file contents. This assumes all files have one row
        with headers and one with values, as all examples are in this format.
    Args:
        full_path: (str) The absolute file path to the csv file to be parsed
    Returns:
        (dict) A dict of key value pairs, the key is column[i]row[0], the value column[i]row[1]
        """
    with open(full_path) as csv_file:
        csvreader = csv.reader(csv_file)
        key_row = next(csvreader)
        value_row = next(csvreader)
        key_value_pairs = dict(zip(key_row, value_row))
        return key_value_pairs


def expand_relevant_data(data):
    """Builds a dictionary of day, value pairs from the csv output. Discards any non-required keys, calls a function
     to flatten ranges.
    Args:
        data: (dict) the output from parse csv. Will ignore unrecognized keys. For example:
            {'mon': 1,
             'tue-thu': 2,
             'fri': 3}
    Returns:
        (dict)
            {'mon': 1,
             'tue': 2,
             'wed': 2,
             'thu': 2,
             'fri': 3}

    """
    day_value_dict = {}
    for k in data.keys():
        if k in days:
            day_value_dict[k] = data[k]
        else:
            # TODO: There is a potential bug where the first day can be before the end day
            range = range_regex.match(k)
            if range:
                day_value_dict = {**day_value_dict, **expand_range(k, data[k])}
    return day_value_dict


def build_output(day_values, description_prefix):
    """Combines the elements of the day, value dictionary and the value of the description field to build the output
        list.
    Args:
        day_values(dict) a dictionary where each day has a key and a value associated with that key.
            {'mon': 1,
             ...
             'fri': 3}
        description_prefix: (str) The value of the description column in the original csv.
    Returns:
        (list) A list of dictionary for. The number of keys should be the same as the input day values, and each
         dictionary in this list should have the following keys, day, description, **action (square or double),
          and value

    """
    final_ouput = []
    for day in days:
        value = int(day_values[day])
        result = action(day, value)
        output_dict = {
            'day': day,
            'description': ' '.join((description_prefix, str(list(result.values())[0]))),
            **result,
            'value': value
        }

        final_ouput.append(output_dict)
    return final_ouput


if __name__ == '__main__':
    for file_name in csv_file_names:
        full_path = ''.join((CSV_DIR, file_name))
        key_value_pair_data = parse_csv(full_path)
        description_prefix = key_value_pair_data.pop('description')
        day_values_dict = expand_relevant_data(key_value_pair_data)
        output = build_output(day_values_dict, description_prefix=description_prefix)
        # I've used json.dumps to try and make the output look a bit nicer, no other reason
        print(file_name)
        print(json.dumps(output, indent=2))
        print('\n')
