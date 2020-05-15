# sys.path.append(os.getcwd() + '/..') # Uncomment for standalone running
from abstract_filter import *
import os.path
import math
import numpy as np


class WordRatio(AbstractFilter):
	def __init__(self):
		self.var_mult = 2

		self.num_of_scans = 1
		self.src_language = ""
		self.trg_language = ""

		self.n = 0.0
		self.sum = 0.0
		self.sum_sq = 0.0

		self.mean = 0.0
		self.var = 0.0

		self.scores = []
		self.thresh = 0.0

		self.model_exist = False

	def initialize(self, source_language, target_language, extra_args):
		self.num_of_scans = 1
		self.src_language = extra_args['source language']
		self.trg_language = extra_args['target language']
		self.normalize = extra_args['normalize scores']
		self.model_filename = "models/WordRatio.stats"
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
				self.mean = float(l[1])
				self.var = float(l[2])

				break

			f.close()
			if self.model_exist:
				print("Loaded stats from the model file.")

		if extra_args['emit scores'] == True:
			self.num_of_scans = 1
		return

	def finalize(self):
		if self.model_exist:
			return

		if self.n == 0:
			self.n += 2.0
		self.mean = self.sum / self.n
		self.var = (self.sum_sq - (self.sum * self.sum) / self.n) / (self.n - 1)
		self.var = math.sqrt(self.var)

		f = open(self.model_filename, 'a')
		lang_pair = self.src_language + self.trg_language
		f.write("\n" + lang_pair + "\n")
		f.write("source\t" + str(self.mean) + "\t" + str(self.var) + "\n")
		f.close()

		self.thresh = np.percentile(self.scores, self.var_mult)

		f = open("quartiles", "a")

		f.write("WordRatio")
		f.write("\t" + str(np.percentile(self.scores, 25)))
		f.write("\t" + str(np.percentile(self.scores, 50)))
		f.write("\t" + str(np.percentile(self.scores, 75)))

		f.write("\n")

		f.close()

	def process_tu(self, tu, num_of_finished_scans):
		src_size = float(len(tu.src_tokens))
		trg_size = float(len(tu.trg_tokens))
		ratio = src_size / max(trg_size, 1.0)

		if self.normalize:
			ratio = min(ratio, 3.0)
			ratio = 1.0 - (abs(1.0 - ratio) / 2.0)

		self.n += 1
		self.sum += ratio
		self.sum_sq += ratio * ratio

		self.scores.append(ratio)

		return [ratio]

	def do_after_a_full_scan(self, num_of_finished_scans):
		return

	def decide(self, tu):
		src_size = float(len(tu.src_tokens))
		trg_size = float(len(tu.trg_tokens))

		if src_size == 0 or trg_size == 0:
			return 'reject'

		ratio = src_size / trg_size
		if self.normalize:
			ratio = min(ratio, 3.0)
			ratio = 1.0 - (abs(1.0 - ratio) / 2.0)

		ratio = abs(ratio - self.mean)

		if ratio <= self.var_mult * self.var:
		# if ratio <= self.thresh:
			return 'accept'
		return 'reject'
