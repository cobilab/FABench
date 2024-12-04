import math
import os
import shutil

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as  plt

best_values = dict()


def update_best_val_dictionary(file, name_tool, weissman_score, compression_ratio):

	if name_tool + "_" + file not in best_values.keys(): #First time the tool is seen
		best_values[name_tool + "_" + file] = [weissman_score, compression_ratio]

	else: #Tool has a position in the dictionary; update pos
		new_weissman = float(best_values[name_tool + "_" + file][0])
		new_compression_ratio = float(best_values[name_tool + "_" + file][1])

		if best_values[name_tool + "_" + file][0] < float(weissman_score):
			new_weissman = weissman_score
		if best_values[name_tool + "_" + file][1] < float(compression_ratio):
			new_compression_ratio = compression_ratio

		best_values[name_tool + "_" + file] = [new_weissman, new_compression_ratio]


def get_std_values(file_content, standard_tool):
	first_line = True

	level_selected = input("Select best level for Weissman score (BZIP2 has to be used as the standard tool)\n")

	for i in file_content:

		if first_line == False:
			if i.startswith(standard_tool + "\t"):
				values = i.split("\n")[0].split("\t")

				if values[8].startswith("./bzip2 -" + level_selected + " -f -k "):
					return float(values[1]), float(values[2]) * 60, values[8]

		else:
			first_line = False

def calc_weissman(standard_tool, alpha):

	num_cases = 3

	#Create the result file and write the first line
	file_res = open("data_all_executions.tsv", "w")
	file_res.write("File\tName tool\tWeissman score\tCompression ratio\tCompressed size\tTime\tSize uncompressed file\tTime ratio\n")

	#For each raw file
	csv_files = []
	for file in os.listdir():
		if file.endswith(".csv"):
			csv_files.append(os.path.join("", file))

	for file in csv_files: #For each file

		first_line = True

		file_access = open(file, "r")
		file_content = file_access.readlines()

		uncompressed_size = os.path.getsize(file.split("_")[1])

		# Get the standard tool information (user has to select the best level, only works with BZIP2 as the standard tool)
		number_bytes_standard, time_standard, best_line = get_std_values(file_content, standard_tool)

		# For all tools, do calculations and write to file
		for i in file_content:

			values = i.split("\n")[0].split("\t")

			name_tool = values[0]
			compressed_size_tool = float(values[1])
			time_tool = float(values[2]) * 60 # Convert to seconds (to avoid log(>1))

			compression_ratio = uncompressed_size / compressed_size_tool
			compression_ratio_standard = uncompressed_size / number_bytes_standard

			weissman_score = alpha * (compression_ratio / compression_ratio_standard) * (math.log10(time_standard) / math.log10(time_tool))

			# "File\tName tool\tWeissman score\tCompression ratio\tCompressed size\tTime\tSize uncompressed file\tTime ratio(time_standard/time_tool)\n"
			file_res.write(file + "\t" + name_tool + "\t" + str(round(weissman_score, num_cases)) + "\t" + str(
				round(compression_ratio, num_cases)) + "\t" + str(
				round(compressed_size_tool, num_cases)) + "\t" + str(round(time_tool, num_cases)) + "\t" + str(
				round(uncompressed_size, num_cases)) + "\t" + str(
				round(time_standard / time_tool, num_cases)) + "\n")

			#Get best values
			update_best_val_dictionary(file, name_tool, weissman_score, compression_ratio)



	file_results = open("best_weissman_comp_ratios.tsv", "w")
	file_results.write("File\tName tool\tBest weissman score\tBest compression ratio\n")

	# Calculate the max compression and decompression memory and the average compression size for each tool (all datasets)
	for i in best_values.keys():
		infos = best_values[i]
		file_results.write(i.split("_")[2] + "\t" + i.split("_")[0] + "\t" + str(infos[0]) + "\t" + str(infos[1]) + "\n")

	file_results.close()


def check_correlations():
	# Read the TSV file into a Pandas DataFrame
	df = pd.read_csv('new_metrics.tsv', sep='\t')

	df = df.drop(['File', 'Name tool'], axis=1)


	# Calculate the correlation matrix
	correlation_matrix = df.corr()

	plt.figure(figsize=(10, 10))
	sns.heatmap(correlation_matrix, annot=True, cmap=sns.diverging_palette(20, 220), vmin=-1, vmax=1)
	plt.show()

	# Print the correlation matrix
	print(correlation_matrix)

	# Get the correlation between specific columns
	column1 = 'Weissman score'
	column2 = 'Compression ratio'
	correlation = df[column1].corr(df[column2])
	print(f"Correlation between {column1} and {column2}: {correlation}")


if __name__ == '__main__':

	directory_path = "results_best_run"
	tool_weissman = "BZIP2"

	if not os.path.exists(directory_path):
		os.makedirs(directory_path)

	calc_weissman(tool_weissman, 1)

	shutil.move("data_all_executions.tsv", directory_path + "/data_all_executions.tsv")
	shutil.move("best_weissman_comp_ratios.tsv", directory_path + "/best_weissman_comp_ratios.tsv")

	#check_correlations()
