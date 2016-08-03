# sys.path.append(os.getcwd() + '/..') # Uncomment for standalone running
from abstract_filter import *
import os.path
import math
import numpy as np


class AlignedProportion(AbstractFilter):
	def __init__(self):
		self.var_mult = 2
		# self.var_mult = 100 - self.var_mult

		self.num_of_scans = 1
		self.src_language = ""
		self.trg_language = ""

		self.n = 0.0

		self.src_sum = 0.0
		self.src_sum_sq = 0.0
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
		self.model_filename = "models/" + extra_args['input filename'] + "__AlignedProportion.stats"
		if self.normalize:
			self.model_filename += "_n"

		if os.path.isfile(self.model_filename):
			self.num_of_scans = 0

			f = open(self.model_filename, 'r')
			l = f.readline().strip().split("\t")
			self.src_mean = float(l[1])
			self.src_var = float(l[2])

			l = f.readline().strip().split("\t")
			self.trg_mean = float(l[1])
			self.trg_var = float(l[2])

			f.close()
			print "Loaded stats from the model file."

		return

	def finalize(self):
		if self.num_of_scans == 0:
			return

		if self.n <= 1:
			self.n = 2.0
		self.src_mean = self.src_sum / self.n
		self.src_var = (self.src_sum_sq - (self.src_sum * self.src_sum) / self.n) / (self.n - 1)
		self.src_var = math.sqrt(self.src_var)

		self.trg_mean = self.trg_sum / self.n
		self.trg_var = (self.trg_sum_sq - (self.trg_sum * self.trg_sum) / self.n) / (self.n - 1)
		self.trg_var = math.sqrt(self.trg_var)

		print "Aligned Proportion:"
		print "source mean & deviation:", self.src_mean, "\t", self.src_var
		print "target mean & deviation:", self.trg_mean, "\t", self.trg_var

		f = open(self.model_filename, 'w')

		f.write("source\t" + str(self.src_mean) + "\t" + str(self.src_var) + "\n")
		f.write("target\t" + str(self.trg_mean) + "\t" + str(self.trg_var) + "\n")

		f.close()

		self.s_thresh = np.percentile(self.src_scores, self.var_mult)
		self.t_thresh = np.percentile(self.trg_scores, self.var_mult)

		f = open("models/quartiles", "a")

		f.write("Aligned Proportion")
		f.write("\t" + str(np.percentile(self.src_scores, 25)))
		f.write("\t" + str(np.percentile(self.src_scores, 50)))
		f.write("\t" + str(np.percentile(self.src_scores, 75)))

		f.write("\t" + str(np.percentile(self.trg_scores, 25)))
		f.write("\t" + str(np.percentile(self.trg_scores, 50)))
		f.write("\t" + str(np.percentile(self.trg_scores, 75)))
		f.write("\n")

		f.close()

	#
	def process_tu(self, tu, num_of_finished_scans):
		src_set = set([x[0] for x in tu.alignment])
		trg_set = set([x[1] for x in tu.alignment])

		src_size = float(len(tu.src_tokens))
		trg_size = float(len(tu.trg_tokens))

		if src_size == 0 or trg_size == 0:
			return [0.0, 0.0]

		self.n += 1
		src_ratio = float(len(src_set)) / src_size
		# if src_ratio > 1:
		# 	print src_set
		# 	print tu.src_tokens
		trg_ratio = float(len(trg_set)) / trg_size
		# if trg_ratio > 1:
		# 	print trg_set
		# 	print tu.trg_tokens

		src_ratio = min(src_ratio, 1.0)
		trg_ratio = min(trg_ratio, 1.0)

		self.src_sum += src_ratio
		self.src_sum_sq += src_ratio * src_ratio
		self.trg_sum += trg_ratio
		self.trg_sum_sq += trg_ratio * trg_ratio

		self.src_scores.append(src_ratio)
		self.trg_scores.append(trg_ratio)

		return [src_ratio, trg_ratio]

	#
	def do_after_a_full_scan(self, num_of_finished_scans):
		pass

	def decide(self, tu):
		src_set = set([x[0] for x in tu.alignment])
		trg_set = set([x[1] for x in tu.alignment])

		src_size = float(len(tu.src_tokens))
		trg_size = float(len(tu.trg_tokens))

		if src_size == 0 or trg_size == 0:
			return 'reject'

		src_ratio = float(len(src_set)) / src_size
		trg_ratio = float(len(trg_set)) / trg_size

		src_ratio = abs(src_ratio - self.src_mean)
		trg_ratio = abs(trg_ratio - self.trg_mean)

		if src_ratio > self.var_mult * self.src_var or trg_ratio > self.var_mult * self.trg_var:
		# if src_ratio < self.s_thresh or trg_ratio < self.t_thresh:
			return 'reject'
		return 'accept'
