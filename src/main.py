import math
import os
import shutil

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

info_weissman = dict()
info_tools = dict()

def calc_weissman(path, standard_tool, alpha):

	num_cases = 3 #Number of round cases in results

	#Create the result file and write the first line
	file_res = open("avg_results_weissman_comp_ratio.tsv", "w")
	file_res.write("File\tName tool\tWeissman score\tCompression ratio\tCompressed size\tTime\tSize uncompressed file\tTime ratio\n")

	#For each of the files created in the last step (with the average compression size)
	for file in os.listdir(path):

		first_line = True

		file_access = open(path + "/" + file, "r")
		file_content = file_access.readlines()

		number_bytes_standard = 0
		time_standard = 0

		uncompressed_size = os.path.getsize(file.split("_")[3:4][0])

		#Get the standard tool information
		for i in file_content:

			if first_line == False:
				if i.startswith(standard_tool + "\t"):

					#If it isn't a header and is the standard tool, get values necessarry to calculate the weissman score
					values = i.split("\n")[0].split("\t")

					number_bytes_standard = float(values[3])
					time_standard = float(values[4]) * 60 #convert to seconds (to avoid log(>1))
			else:
				first_line = False

		first_line = True

		#For all tools, do calculations and write to file
		for i in file_content:

			if first_line == False:
				values = i.split("\n")[0].split("\t")

				name_tool = values[0]
				compressed_size_tool = float(values[3])
				time_tool = float(values[4]) * 60 #convert to seconds (to avoid log(>1))

				compression_ratio = uncompressed_size / compressed_size_tool
				compression_ratio_standard = uncompressed_size / number_bytes_standard

				weissman_score = alpha * (compression_ratio / compression_ratio_standard) * (math.log10(time_standard) / math.log10(time_tool))

				#"File\tName tool\tWeissman score\tCompression ratio\tCompressed size\tTime\tSize uncompressed file\tTime ratio(time_standard/time_tool)\n"
				file_res.write(file + "\t" + name_tool + "\t" + str(round(weissman_score, num_cases)) + "\t" + str(round(compression_ratio, num_cases)) + "\t" + str(round(compressed_size_tool, num_cases)) + "\t" + str(round(time_tool, num_cases)) + "\t" + str(round(uncompressed_size, num_cases))  + "\t" + str(round(time_standard/time_tool, num_cases)) + "\n")
			else:
				first_line = False


def add_vals_to_dict(name_tool, max_comp, max_decomp, avg_num_bytes):

	if name_tool not in info_tools.keys(): #First time the tool is seen
		info_tools[name_tool] = [max_comp, max_decomp, avg_num_bytes]
	else: #Tool has a position in th edictionary; update pos
		infos = info_tools[name_tool]

		new_val_max_comp = max(infos[0], max_comp)
		new_val_max_decomp = max(infos[1], max_decomp)
		new_avg_num_bytes = infos[2] + avg_num_bytes

		info_tools[name_tool] = [new_val_max_comp, new_val_max_decomp, new_avg_num_bytes]


def update_vars(max_comp, max_decomp, num_bytes, time, count, list_vals):
	max_comp = max(max_comp, float(list_vals[3]))
	max_decomp = max(max_decomp, float(list_vals[5]))
	num_bytes += float(list_vals[1])
	time += float(list_vals[2])
	count += 1

	return max_comp, max_decomp, num_bytes, time, count

def write_and_reset_vars(tex_file, name_tool, max_comp, max_decomp, num_bytes, time, count):

	#Write singular dataset results
	tex_file.write(
		str(name_tool) + "\t" + str(max_comp) + "\t" + str(max_decomp) + "\t" + str(num_bytes / count) + "\t" + str(
			time / count) + "\t" + str(count) + "\n")

	#Update the dictionary with the results of all datasets
	add_vals_to_dict(name_tool, max_comp, max_decomp, num_bytes / count)

	#Reset variables
	return 0, 0, 0, 0, 0


def import_files_in_dir(path):

	name_tool = ""
	max_comp = 0
	max_decomp = 0
	num_bytes = 0
	time = 0
	count = 0

	csv_files = []

	# Select raw data files
	for file in os.listdir():
		if file.endswith(".csv"):
			csv_files.append(os.path.join("", file))

	# Calculate the max compression and decompression memory and the average compression size for each tool in each dataset
	for file_name in csv_files:
		file = open(file_name, "r")

		tex_file = open("tables_results_" + file_name + ".tsv", "w")
		tex_file.write("Name tool\tMax_comp_mem\tMax_decomp_mem\tAvg_bytes\tAvg_time\tNumber_executions\n")

		for line in file:

			line = line.strip("\n")
			list_vals = line.split("\t") # Get the information of a row in an array

			curr_tool = list_vals[0] #Check name of tool in current row

			if name_tool == "" or curr_tool == name_tool: #First tool in the file or continuation of the results

				if name_tool == "":
					name_tool = curr_tool

				#Update info
				max_comp, max_decomp, num_bytes, time, count = update_vars(max_comp, max_decomp, num_bytes, time, count, list_vals)

			else: #New tool is seen; write results and reset variables

				max_comp, max_decomp, num_bytes, time, count = write_and_reset_vars(tex_file, name_tool, max_comp, max_decomp, num_bytes, time, count)
				max_comp, max_decomp, num_bytes, time, count = update_vars(max_comp, max_decomp, num_bytes, time, count, list_vals)

				name_tool = curr_tool

		#Write results for the last tool in the file
		max_comp, max_decomp, num_bytes, time, count = write_and_reset_vars(tex_file, name_tool, max_comp, max_decomp,
		                                                                    num_bytes, time, count)
		name_tool = ""


		#Close result file and move results to different directory
		file.close()
		tex_file.close()
		shutil.move("tables_results_" + file_name + ".tsv", path + "/tables_results_" + file_name + ".tsv")

	file_results = open("plot_data_mem_comp_size.tsv", "w")
	file_results.write("Name tool\tMax_comp_mem\tMax_decomp_mem\tAverage_bytes\n")

	#Get the max compression and decompression memory and the average compression size for each tool (all datasets)
	for i in info_tools.keys():
		infos = info_tools[i]
		file_results.write(i + "\t" + str(infos[0]) + "\t" + str(infos[1]) + "\t" + str(infos[2]) + "\n")

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

	directory_path = "results_avg"
	tool_weissman = "BZIP2"

	if not os.path.exists(directory_path):
		os.makedirs(directory_path)

	import_files_in_dir(directory_path) #calculates the basic metrics

	'''for i in range(1,11):

		calc_weissman(directory_path, tool_weissman, i/10)'''
	calc_weissman(directory_path, tool_weissman, 1)

	if not os.path.exists(directory_path + "/final_tsv"):
		os.makedirs(directory_path + "/final_tsv")

	shutil.move("avg_results_weissman_comp_ratio.tsv", directory_path + "/final_tsv/avg_results_weissman_comp_ratio.tsv")
	shutil.move("plot_data_mem_comp_size.tsv", directory_path + "/final_tsv/plot_data_mem_comp_size.tsv")

	#check_correlations()
