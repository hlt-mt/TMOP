# sys.path.append(os.getcwd() + '/..') # Uncomment for standalone running
from abstract_filter import *
import os.path
import math
import numpy as np


class WordLength(AbstractFilter):
	def __init__(self):
		self.var_mult = 2

		self.num_of_scans = 0
		self.src_language = ""
		self.trg_language = ""

		self.tokenizer = None

		self.src_n = 0.0
		self.src_sum = 0.0
		self.src_sum_sq = 0.0
		self.trg_n = 0.0
		self.trg_sum = 0.0
		self.trg_sum_sq = 0.0

		self.src_mean = 0.0
		self.src_var = 0.0
		self.trg_mean = 0.0
		self.trg_var = 0.0

		self.src_scores = []
		self.trg_scores = []
		self.s_thresh = 0.0
		self.t_thresh = 0.0

	#
	def initialize(self, source_language, target_language, extra_args):
		self.num_of_scans = 1
		self.src_language = extra_args['source language']
		self.trg_language = extra_args['target language']
		self.normalize = extra_args['normalize scores']
		self.model_filename = "models/WordLength.stats"
		if self.normalize:
			self.model_filename += "_n"

		if os.path.isfile(self.model_filename):
			lang_pair = self.src_language + self.trg_language
			f = open(self.model_filename, 'r')

			l = f.readline()
			while l:
				if lang_pair not in l:
					l = f.readline()
					continue

				# found the statistics
				self.model_exist = True
				self.num_of_scans = 0

				l = f.readline().strip().split("\t")
				self.src_mean = float(l[1])
				self.src_var = float(l[2])

				l = f.readline().strip().split("\t")
				self.trg_mean = float(l[1])
				self.trg_var = float(l[2])

				break

			f.close()
			if self.model_exist:
				print "Loaded stats from the model file."

		if extra_args['emit scores'] == True:
			self.num_of_scans = 1
		return

	def finalize(self):
		if self.model_exist:
			return

		if self.src_n == 0:
			self.src_n += 2.0
		self.src_mean = self.src_sum / self.src_n
		self.src_var = (self.src_sum_sq - (self.src_sum * self.src_sum) / self.src_n) / (self.src_n - 1)
		self.src_var = math.sqrt(self.src_var)

		if self.trg_n == 0:
			self.trg_n += 2.0
		self.trg_mean = self.trg_sum / self.trg_n
		self.trg_var = (self.trg_sum_sq - (self.trg_sum * self.trg_sum) / self.trg_n) / (self.trg_n - 1)
		self.trg_var = math.sqrt(self.trg_var)

		f = open(self.model_filename, 'a')
		lang_pair = self.src_language + self.trg_language
		f.write("\n" + lang_pair + "\n")

		f.write("source\t" + str(self.src_mean) + "\t" + str(self.src_var) + "\n")
		f.write("target\t" + str(self.trg_mean) + "\t" + str(self.trg_var) + "\n")

		f.close()

		self.s_thresh = np.percentile(self.src_scores, self.var_mult)
		self.t_thresh = np.percentile(self.trg_scores, self.var_mult)

	#
	def process_tu(self, tu, num_of_finished_scans):
		for word in tu.src_tokens:
			self.src_n += 1
			self.src_sum += len(word)
			self.src_sum_sq += len(word) * len(word)

			self.src_scores.append(len(word))

		for word in tu.trg_tokens:
			self.trg_n += 1
			self.trg_sum += len(word)
			self.trg_sum_sq += len(word) * len(word)

			self.trg_scores.append(len(word))

	def do_after_a_full_scan(self, num_of_finished_scans):
		pass

	def decide(self, tu):
		src_ool_words = 0  # Out of Length words
		trg_ool_words = 0  # Out of Length words

		for word in tu.src_tokens:
			tmp = abs(len(word) - self.src_mean)

			if tmp > self.var_mult * self.src_var:
				src_ool_words += 1

		for word in tu.trg_tokens:
			tmp = abs(len(word) - self.trg_mean)

			if tmp > self.var_mult * self.trg_var:
				trg_ool_words += 1

		if src_ool_words > 0 or trg_ool_words > 0:
			return 'reject'
		return 'accept'
