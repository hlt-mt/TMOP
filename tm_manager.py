import os
import re
import sys
import json
import codecs
import inspect
import threading
from copy import copy
# from filters.abstract_filter import TU

"""
TMoP - Translation Memory Open-Source Purifier by Matteo Negri, Masoud Jalili Sabet and Marco Turchi, October 2015

Based on research by Matteo Negri, Masoud Jalili Sabet and Marco Turchi.

Copyright 2015 Matteo Negri, Masoud Jalili Sabet and Marco Turchi.  <negri@fbk.eu>, <jalili.masoud@gmail.com> and <turchi@fbk.eu>. All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are
permitted provided that the following conditions are met:

   1. Redistributions of source code must retain the above copyright notice, this list of
      conditions and the following disclaimer.

   2. Redistributions in binary form must reproduce the above copyright notice, this list
      of conditions and the following disclaimer in the documentation and/or other materials
      provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER ``AS IS'' AND ANY EXPRESS OR IMPLIED
WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those of the
authors and should not be interpreted as representing official policies, either expressed
or implied, of the copyright holder.
"""

class TMManager:
	"""
	This class manages all filters based on config file. After calling run() method,
	it will start the process of cleaning the translation units.
	"""

	#
	def __init__(self, conf_file_name=""):
		# Adding filter folder to path. after this filters can import 'AbstractFilter'.
		sys.path.append(os.getcwd() + '/filters/')
		sys.path.append(os.getcwd() + '/policies/')

		# This is an array of instances from active filters.
		# each entry is a tuple of the form (filter_name, filter_object, num_of_scans).
		self.filters = []

		# This is an array of instances from active decision policies.
		# each entry is a tuple of the form (policy_name, policy_object).
		self.policies = []

		# The handlers of all the output files are kept in this dictionary.
		# The Keys are the names of files and the values are handlers.
		self.output_files = {}

		# After parsing the config file, these variables are filled with corresponding options.
		self.options = None
		self.filters_config = None
		self.policies_config = None
		self.have_alignment = False
		self.have_token = False
		self.create_out_files = True

		self.config_file_name = conf_file_name

	#
	def load_options_from_config_file(self):
		"""
		This function reads the config file and extracts the information about how the tm_manager should work.
		After calling this function, the input file, the output file and the policy is determined.

		@rtype: int
		@return: returns 0 if there is no error. otherwise, returns error number.
		"""

		print "Loading Options fro the config file ...\n"

		if self.config_file_name:
			conf_file = open(self.config_file_name)
		else:
			conf_file = open("config.json")
		try:
			config = json.load(conf_file)
		except ValueError:
			print "--------------------------------------------"
			print "The loader could not decode the config file."
			print "The config file should be in JSON format."
			print "--------------------------------------------\n"
			return 1

		conf_file.close()
		# --------------------

		if 'options' not in config:
			print "There is no object called 'options' in the config file."
			return 2
		self.options = config['options']
		if 'input file' not in self.options or len(self.options['input file']) < 1:
			print "The 'input file' is not indicated in config file."
			return 21

		if 'source language' not in self.options or 'target language' not in self.options:
			print "The languages are not indicated in config file."
			return 22
		if 'output folder' not in self.options:
			print "The 'output folder' is not indicated in config file. It is set to default('output')."
			self.options['output folder'] = "output"

		self.have_alignment = False
		if 'align file' in self.options:
			self.have_alignment = True

		self.have_token = False
		if 'token file' in self.options:
			self.have_token = True

		self.create_out_files = True
		if 'no out files' in self.options:
			if self.options['no out files'].lower() in ['true', 'yes', 'ok']:
				self.create_out_files = False

		self.normalize_scores = False
		if 'normalize scores' in self.options:
			if self.options['normalize scores'].lower() in ['true', 'yes', 'ok']:
				self.normalize_scores = True

		self.have_scores = False
		if 'emit scores' in self.options:
			if self.options['emit scores'].lower() in ['true', 'yes', 'ok']:
				self.have_scores = True

		# making the output folder
		path = os.getcwd() + "/" + self.options['output folder']
		if not os.path.isdir(path):
			os.makedirs(path)
		# --------------------

		if 'policies' not in config:
			print "There is no object called 'policies' in the config file."
			return 3
		self.policies_config = config['policies']
		# --------------------

		if 'filters' not in config:
			print "There is no object called 'filters' in the config file."
			return 4
		self.filters_config = config['filters']
		# --------------------

		print "\nDone."
		return 0

	#
	def load_filters(self):
		"""
		In this part, filter names are extracted from the config file,
		and after importing them, instances are made from each filter for further use.
		After calling this method, the filters instances are appended to 'self.filters' array.
		"""
		print "Loading Filters ..."

		self.filters = []
		from abstract_filter import AbstractFilter

		# path is absolute path of filters folder
		path = os.getcwd() + '/filters/'

		for option in self.filters_config:
			if option[1] != "on":
				continue

			print "----------"

			# Checking for existence of the folder for each filter
			filter_name = option[0]
			if not os.path.exists(path + filter_name):
				print "There is no folder with name " + filter_name
				print "The expected path of the filter:\n", path + filter_name
				continue

			sys.path.append(path + filter_name)
			# filter_module = __import__(filter_name)
			__import__(filter_name)

			# Extracting Classes from the module
			module_classes = inspect.getmembers(sys.modules[filter_name], inspect.isclass)

			# Finding the base class of the filter
			module_classes = [x for x in module_classes if x[0] == filter_name]
			if len(module_classes) == 0:
				print "There is no class named '" + filter_name + "' in the '" + filter_name + ".py' file."
				continue

			# Instantiating from the filter class
			try:
				filter_class = module_classes[0][1]

				# Checking if the filter is a subclass of AbstractFilter.
				if not issubclass(filter_class, AbstractFilter):
					print "The filter", filter_name, "is not a subclass of AbstractFilter."
					continue

				filter_object = filter_class()

				self.filters.append((filter_name, filter_object, -1))
				print "The filter", filter_name, "is ready and active."
			except Exception, e:
				print "Couldn't make instance from " + filter_name
				print "The Exception:"
				print repr(e)
				continue

		print "\nDone.\n----------\n"

	#
	def load_policies(self):
		"""
		In this part, policies names are extracted from the config file,
		and after importing them, instances are made from each policy for further use.
		After calling this method, the policies instances are appended to 'self.policies' array.
		"""
		print "Loading Policies ..."

		self.policies = []
		from abstract_policy import AbstractPolicy

		# path is absolute path of filters folder
		path = os.getcwd() + '/policies/'

		for option in self.policies_config:
			if option[1] != "on":
				continue

			print "----------"

			# Checking for existence of the folder for each filter
			policy_name = option[0]
			if not os.path.exists(path + policy_name):
				print "There is no folder with name " + policy_name
				print "The expected path of the policy:\n", path + policy_name
				continue

			sys.path.append(path + policy_name)
			# filter_module = __import__(filter_name)
			__import__(policy_name)

			# Extracting Classes from the module
			module_classes = inspect.getmembers(sys.modules[policy_name], inspect.isclass)

			# Finding the base class of the policy
			module_classes = [x for x in module_classes if x[0] == policy_name]
			if len(module_classes) == 0:
				print "There is no class named '" + policy_name + "' in the '" + policy_name + ".py' file."
				continue

			# Instantiating from the policy class
			try:
				policy_class = module_classes[0][1]

				# Checking if the policy is a subclass of AbstractPolicy.
				if not issubclass(policy_class, AbstractPolicy):
					print "The policy", policy_name, "is not a subclass of AbstractPolicy."
					continue

				policy_object = policy_class()

				self.policies.append((policy_name, policy_object))
				print "The policy", policy_name, "is ready and active."
			except Exception, e:
				print "Couldn't make instance from " + policy_name
				print "The Exception:"
				print repr(e)
				continue

		print "\nDone.\n----------\n"

	#
	def policy_check_for_tu(self, tu_string, results):
		self.output_files['log'].write(tu_string.split('\t')[0] + '\t')
		for policy_tuple in self.policies:
			try:
				answer = policy_tuple[1].decide(results)
			except Exception, e:
				print "There is a problem with decision making in policy " + policy_tuple[0]
				print "The Exception:"
				print repr(e)
				answer = 'no_answer'

			# ----- Writing the results in separate files -----
			if self.create_out_files:
				if (answer + "_" + policy_tuple[0]) not in self.output_files:
					path = os.getcwd() + "/" + self.options['output folder'] + "/"
					out_file_name = path + answer + "_" + policy_tuple[0] + "__" + self.options['input file']

					out_file = open(out_file_name, 'w')
					self.output_files[(answer + "_" + policy_tuple[0])] = out_file

				self.output_files[(answer + "_" + policy_tuple[0])].write(tu_string + "\n")

			if answer == 'reject':
				self.output_files['log'].write('0\treject\t')
			elif answer == 'accept':
				self.output_files['log'].write('2\taccept\t')
			else:
				self.output_files['log'].write('1\t' + answer + '\t')

		for r in results:
			self.output_files['log'].write('\t#|#\t' + r[0] + '\t' + r[1])

		self.output_files['log'].write('\n')

	#
	def close_output_files(self):
		for name, handler in self.output_files.iteritems():
			handler.close()

	#
	def run(self):
		"""
		This function has 3 sections. In the first section it calls initializer functions to prepare the tm_manager.
		In the second section, 'Learning Section', TM input is scanned for several times for the
		filters functions which are called and the input data is given to them.
		In the last section, 'Decision Section', each Translation Unit is given to all filters and the results are
		stored in the 'results' array. The policy_check_for_tu() is then called with the results array as the input
		and the output of that function indicates whether the TU should be deleted or not.
		"""
		print "Running the TM cleaner ..."
		from abstract_filter import TU

		if self.load_options_from_config_file() > 0:
			print "Exiting before finishing."
			print "-------------------------"
			return
		self.load_filters()
		self.load_policies()

		# Clearing the arrays
		self.close_output_files()
		self.output_files = {}

		print "Initializing the filters..."

		filters_arguments = {}
		filters_arguments["source language"] = self.options['source language']
		filters_arguments["target language"] = self.options['target language']
		filters_arguments["input filename"] = self.options['input file']
		filters_arguments["normalize scores"] = self.normalize_scores
		filters_arguments["emit scores"] = self.have_scores

		for i in range(len(self.filters)):
			try:
				# intializing the filters
				self.filters[i][1].initialize(self.options['source language'], self.options['target language'], copy(filters_arguments))
				# updating the number of scans
				self.filters[i] = (self.filters[i][0], self.filters[i][1], self.filters[i][1].num_of_scans)
			except Exception, e:
				print "Couldn't initialize the filter", self.filters[i][0]
				print "This filter is excluded from the active filters."
				print "The Exception:"
				print repr(e)
				self.filters[i] = (self.filters[i][0], self.filters[i][1], -1)

		# Removing the excluded filters.
		self.filters = [f_tuple for f_tuple in self.filters if f_tuple[2] >= 0]

		if len(self.filters) == 0:
			print "There are no active filters."
			print "Exiting before finishing."
			print "-------------------------"
			return

		# ---------- Learning Section ----------
		print "Learning Section :"
		print "======================================================================"

		# Finding maximum number of scans required for filters.
		max_scan = 0
		for filter_tuple in self.filters:
			max_scan = max(max_scan, filter_tuple[2])

		print "\nNumber of active filters:", len(self.filters)
		print "Number of scans needed:", max_scan
		print "-----------------------"

		# Extending the input URL
		input_file_path = os.getcwd() + '/data/' + self.options['input file']

		if not os.path.isfile(input_file_path):
			print "Input file not found!\nGiven file in config file:", input_file_path
			print "Exiting the code."
			return

		if self.have_alignment:
			align_file_path = os.getcwd() + '/data/' + self.options['align file']

			if not os.path.isfile(align_file_path):
				print "Alignment file not found!\nGiven file in config file:", align_file_path
				print "Exiting the code."
				return

		# For tokenizing the TUs and put the output in TU objects
		if self.have_token:
			token_file_path = os.getcwd() + '/data/' + self.options['token file']

			if not os.path.isfile(token_file_path):
				print "Token file not found!\nGiven file in config file:", token_file_path
				print "Exiting the code."
				return
		else:
			tokenizer = re.compile(r"\(|\)|\w+|\$[\d\.]+|\S+")

		if self.have_scores:
			out_path = os.getcwd() + "/" + self.options['output folder'] + "/"
			score_file_name = out_path + "scores__" + self.options['input file']
			score_file = open(score_file_name, "w")
			score_file.close()

		for scan_number in range(max_scan):
			print "Scan iteration ", scan_number + 1, ":"
			active_filters = [(x[0], x[1], x[2]-(max_scan-scan_number)) for x in self.filters if x[2] >= max_scan-scan_number]

			# The input file is in CSV Tab separated format.
			tm_file = open(input_file_path, 'rb')
			if self.have_alignment is True:
				tm_align_file = open(align_file_path, 'r')
			if self.have_token is True:
				tm_token_file = open(token_file_path, 'rb')

			line_no = 0
			for line in tm_file:
				line_no += 1
				line = line.split("\t")

				if self.have_alignment is True:
					alignment = tm_align_file.readline()
					alignment = alignment.strip().split(" ")
					alignment = [x.split('-') for x in alignment if x != '']

				if len(line) != 3:
					print "Invalid translation unit at line ", line_no
					continue

				# The 1st and 2nd elements of each line are phrases from source and target language.
				line[1] = line[1].strip()
				line[2] = line[2].strip()
				tu = TU()
				try:
					if type(line[1]) != unicode:
						tu.src_phrase = line[1].decode("utf-8")
					else:
						tu.src_phrase = line[1]

					if type(line[2]) != unicode:
						tu.trg_phrase = line[2].decode("utf-8")
					else:
						tu.trg_phrase = line[2]

					if self.have_token is True:
						token_line = tm_token_file.readline()
						token_line = token_line[:-1].lower().split("\t")

						tu.src_tokens = token_line[0].split()
						tu.trg_tokens = token_line[1].split()
					else:
						tu.src_tokens = tokenizer.findall(tu.src_phrase.lower())
						tu.trg_tokens = tokenizer.findall(tu.trg_phrase.lower())

					if self.have_alignment is True:
						tu.alignment = [(int(x[0]), int(x[1])) for x in alignment]

				except UnicodeEncodeError as err:
					print ("[" + str(err.start) + ", " + str(err.end) + "]"), err.object[err.start:err.end]
					print err.object
					print "--", err.reason
					# print "-- The translation unit in line", line_no, "is corrupted. Skipped"
					continue
				except Exception, e:
					print repr(e)
					# print "The translation unit in line", line_no, "is corrupted. Skipped"
					continue

				scores = []
				for filter_tuple in active_filters:
					try:
						score = filter_tuple[1].process_tu(copy(tu), filter_tuple[2])
						if score is not None:
							scores.append(score)
					except Exception, e:
						print "The filter", filter_tuple[0], "has problems processing the TU in line:", line_no
						print "The Exception:"
						print repr(e)

				# writing filters' scores in the scores file
				if self.have_scores and (max_scan - scan_number <= 1):
					out_path = os.getcwd() + "/" + self.options['output folder'] + "/"
					score_file_name = out_path + "scores__" + self.options['input file']
					score_file = open(score_file_name, "a")

					scores = str(scores).replace("[", "").replace("]", "").replace(" ", "")
					score_file.write(scores + "\n")

					score_file.close()

			# closing data files
			tm_file.close()
			if self.have_alignment is True:
				tm_align_file.close()
			if self.have_token is True:
				tm_token_file.close()

			# Finishing the scan for all active filters.
			for filter_tuple in active_filters:
				filter_tuple[1].do_after_a_full_scan(filter_tuple[2] + 1)

		# Finalizing all filters.
		for i in range(len(self.filters)):
			try:
				self.filters[i][1].finalize()
			except Exception, e:
				print "The filter " + self.filters[i][0] + " had problems in finalizing. Excluded from decision section."
				print "The Exception:"
				print repr(e)
				self.filters[i] = (self.filters[i][0], self.filters[i][1], -1)

		# Removing excluded filters.
		self.filters = [f_tuple for f_tuple in self.filters if f_tuple[2] >= 0]

		if len(self.filters) == 0:
			print "There are no active filters."
			print "Exiting before finishing."
			print "-------------------------"
			return
		print "-----------------------\n"

		# ---------- Decision Section ----------
		print "Decision Section :"
		print "======================================================================"

		# Extending the input URL
		input_file_path = os.getcwd() + '/data/' + self.options['input file']

		# Making an output file for skipped TUs
		out_path = os.getcwd() + "/" + self.options['output folder'] + "/"
		out_file_name = out_path + "skipped__" + self.options['input file']

		out_file = open(out_file_name, 'w')
		self.output_files['skipped'] = out_file

		# Making an output file for all the decisions made
		out_path = os.getcwd() + "/" + self.options['output folder'] + "/"
		out_file_name = out_path + "decision_log__" + self.options['input file']

		out_file = open(out_file_name, 'w')
		self.output_files['log'] = out_file

		tm_file = open(input_file_path, 'rb')
		if self.have_alignment is True:
			tm_align_file = open(align_file_path, 'r')
		if self.have_token is True:
			tm_token_file = open(token_file_path, 'rb')

		line_no = 0
		for line in tm_file:
			line_no += 1
			line = line.split("\t")

			# Exiting the decision section for the rest of the TM
			if 'max decision' in self.options:
				if self.options['max decision'] >= 0 and self.options['max decision'] < line_no:
					break

			if self.have_alignment is True:
				alignment = tm_align_file.readline()
				alignment = alignment.strip().split(" ")
				alignment = [x.split('-') for x in alignment if x != '']

			if len(line) != 3:
				print "Invalid translation unit at line ", line_no
				self.output_files['skipped'].write("invalid\t" + "\t".join(line) + "\n")
				self.output_files['log'].write('-1\tskipped\n')
				continue

			# The 1st and 2nd elements of each line are phrases from source and target language.
			line[1] = line[1].strip()
			line[2] = line[2].strip()
			tu = TU()
			try:
				# tu.src_phrase = line[1].decode("utf-8")
				# tu.trg_phrase = line[2].decode("utf-8")
				if type(line[1]) != unicode:
					tu.src_phrase = unicode(line[1], "utf-8")
					# tu.src_phrase = line[1].decode("utf-8")
				else:
					tu.src_phrase = line[1]

				if type(line[2]) != unicode:
					tu.trg_phrase = unicode(line[2], "utf-8")
					# tu.trg_phrase = line[2].decode("utf-8")
				else:
					tu.trg_phrase = line[2]

				if self.have_token is True:
					token_line = tm_token_file.readline()
					token_line = token_line[:-1].lower().split("\t")

					tu.src_tokens = token_line[0].split()
					tu.trg_tokens = token_line[1].split()
				else:
					tu.src_tokens = tokenizer.findall(tu.src_phrase.lower())
					tu.trg_tokens = tokenizer.findall(tu.trg_phrase.lower())

				if self.have_alignment is True:
					tu.alignment = [(int(x[0]), int(x[1])) for x in alignment]

			except Exception, e:
				print repr(e)
				self.output_files['skipped'].write("\t".join(line) + "\n")
				self.output_files['log'].write('-1\tskipped\n')
				# print "The translation unit in line", line_no, "is corrupted. Skipped"
				continue
			# except:
			# 	print "The translation unit in line", line_no, "is corrupted. Skipped"
			# 	self.output_files['skipped'].write("\t".join(line) + "\n")
			# 	continue

			# results is an array of tuples of the form (filter name, filter answer).
			results = []
			# Giving the tu to all active filters in this scan.
			for filter_tuple in self.filters:
				answer = filter_tuple[1].decide(copy(tu))
				results.append((filter_tuple[0], answer))

			self.policy_check_for_tu("\t".join(line), results)
			# final_answer = self.policy_check_for_tu(results)
			# if final_answer:
			# 	output_file.write("\t".join(line))

		# closing data files
		tm_file.close()
		if self.have_alignment is True:
			tm_align_file.close()
		if self.have_token is True:
			tm_token_file.close()
		self.close_output_files()

		print "Cleaning is finished."
		print "======================================================================"
		print "======================================================================"
