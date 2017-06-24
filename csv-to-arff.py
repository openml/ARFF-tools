"""
This script converts csv datasets to ARFF format.
In the ARFF format, one needs to know whether features are numeric or categorical - this is done with a simple heuristic, and thus is not always completely accurate.
"""
import sys
import math
import numpy
import pandas as pd
import numbers

def list_only_int(lst):
	return (all([isinstance(el, numbers.Number) for el in lst]) and
		all([math.isnan(el) or float(el).is_integer() for el in lst]))

input_file = sys.argv[1]
output_file = sys.argv[2]

if '/' in input_file:
	end_of_folder_path = input_file.rfind('/') + 1
else:
	end_of_folder_path = 0

dataset_name = input_file[end_of_folder_path:-4]
dataset = pd.read_csv(input_file, sep='\t')

column_info = []
integer_columns = []
for column in dataset.columns:
	column_values = dataset[column]
	row_is_integer = list_only_int(column_values)
	integer_columns.append(row_is_integer)
	not_nan_values = column_values[~numpy.isnan(column_values)]
	unique_values = numpy.unique(not_nan_values)
	is_categorical = (len(unique_values) <= 10 and row_is_integer)
	if is_categorical:
		data_type_str = '{{{}}}'.format(','.join([str(int(val)) for val in unique_values]))
	else:
		data_type_str = 'NUMERIC'
	column_info.append((column, data_type_str))

with open('{}.arff'.format(dataset_name), 'w') as arff_file:
	arff_file.write('% This ARFF is automatically generated.\n'
			'% The data types of attributes are inferred from the data.\n'
			'% In particular this means there is some uncertainty as to whether '
			'an attribute truly is categorical, numerical or ordinal.\n'
			'\n'
			'@RELATION {}\n'.format(dataset_name))
	for (name, data_type) in column_info:
		arff_file.write('@ATTRIBUTE {} {}\n'.format(name.replace(' ', '_'), data_type))

	arff_file.write('@DATA\n')
	for row in dataset.as_matrix():
		row_str_els = []
		for column, el in enumerate(row):
			if not math.isnan(el) and integer_columns[column]:
				el = int(el)
			row_str_els.append(str(el))
		row_str = ','.join([el for el in row_str_els])
		arff_file.write('{}\n'.format(row_str))
