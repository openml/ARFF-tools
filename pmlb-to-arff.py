"""
This script converts the datasets of PMLB to ARFF format.
In the ARFF format, one needs to know whether features are numeric or categorical - this is done with a simple heuristic, and thus is not always completely accurate.
"""
import sys
import math
import numpy
from pmlb import fetch_data
pmlb_cache_dir = '../experiments/data/'

def list_only_int(lst):
	row_is_integer = True
	for el in lst:
		is_int = False
		try:
			if math.isnan(el):
				is_int = True
			else:
				is_int = float(el).is_integer()
		except:
			pass
		finally:
			row_is_integer &= is_int
	return row_is_integer

dataset_name = sys.argv[1]
dataset = fetch_data(dataset_name, local_cache_dir=pmlb_cache_dir)

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

with open('output_folder/{}.arff'.format(dataset_name), 'w') as arff_file:
	arff_file.write('% This dataset is taken from the Penn Machine Learning Benchmark.\n'
			'% This ARFF is automatically generated.\n'
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
