# sys.path.append(os.getcwd() + '/..') # Uncomment for standalone running
from abstract_filter import *
import os.path
import math
import numpy as np


class AlignedSequenceLength(AbstractFilter):
	def __init__(self):
		self.var_mult = 2
		# self.var_mult = 100 - self.var_mult

		self.num_of_scans = 1
		self.src_language = ""
		self.trg_language = ""

		self.src_n = 0.0
		self.trg_n = 0.0

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
		self.model_filename = "models/AlignedSequenceLength.stats"
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

		if self.src_n <= 1:
			self.src_n = 2.0
		self.src_mean = self.src_sum / self.src_n
		self.src_var = (self.src_sum_sq - (self.src_sum * self.src_sum) / self.src_n) / (self.src_n - 1)
		self.src_var = math.sqrt(self.src_var)

		if self.trg_n <= 1:
			self.trg_n = 2.0
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

		f = open("models/quartiles", "a")

		f.write("AlignedSequenceLength")
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

		src_bar = set([i for i in range(int(src_size))])
		trg_bar = set([i for i in range(int(trg_size))])
		src_set = src_bar - src_set
		trg_set = trg_bar - trg_set

		last = -1
		n = 0.0
		smean = 0.0
		for current in src_set:
			if current - last > 1:
				n += 1
				smean += (current - last - 1)
			last = current
		if src_size - last > 1:
			n += 1
			smean += (src_size - last - 1)

		smean /= max(n, 1.0)
		if self.normalize:
			smean = min(smean, 4.0) / 4.0

		self.src_n += 1
		self.src_sum += smean
		self.src_sum_sq += smean * smean

		last = -1
		n = 0.0
		tmean = 0.0
		for current in trg_set:
			if current - last > 1:
				n += 1
				tmean += (current - last - 1)
			last = current
		if trg_size - last > 1:
			n += 1
			tmean += (trg_size - last - 1)

		tmean /= max(n, 1.0)
		if self.normalize:
			tmean = min(tmean, 4.0) / 4.0

		self.trg_n += 1
		self.trg_sum += tmean
		self.trg_sum_sq += tmean * tmean

		self.src_scores.append(smean)
		self.trg_scores.append(tmean)

		return [smean, tmean]

	#
	def do_after_a_full_scan(self, num_of_finished_scans):
		pass

	def decide(self, tu):
		src_set = set([x[0] for x in tu.alignment])
		trg_set = set([x[1] for x in tu.alignment])
		src_size = float(len(tu.src_tokens))
		trg_size = float(len(tu.trg_tokens))

		src_bar = set([i for i in range(int(src_size))])
		trg_bar = set([i for i in range(int(trg_size))])
		src_set = src_bar - src_set
		trg_set = trg_bar - trg_set

		n = 0.0
		src_mean = 0.0
		last = -1
		for current in src_set:
			if current - last > 1:
				n += 1
				src_mean += (current - last - 1)
			last = current
		if src_size - last > 1:
			n += 1
			src_mean += (src_size - last - 1)
		if n < 1:
			n = 1.0
		src_mean /= n
		if self.normalize:
			src_mean = min(src_mean, 4.0) / 4.0

		n = 0.0
		trg_mean = 0.0
		last = -1
		for current in trg_set:
			if current - last > 1:
				n += 1
				trg_mean += (current - last - 1)
			last = current
		if trg_size - last > 1:
			n += 1
			trg_mean += (trg_size - last - 1)
		if n < 1:
			n = 1.0
		trg_mean /= n
		if self.normalize:
			trg_mean = min(trg_mean, 4.0) / 4.0

		src_mean = abs(src_mean - self.src_mean)
		trg_mean = abs(trg_mean - self.trg_mean)

		if src_mean > self.var_mult * self.src_var or trg_mean > self.var_mult * self.trg_var:
		# if src_mean < self.s_thresh or trg_mean < self.t_thresh:
			return 'reject'
		return 'accept'
