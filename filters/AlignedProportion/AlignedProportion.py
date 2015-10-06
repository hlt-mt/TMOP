# sys.path.append(os.getcwd() + '/..') # Uncomment for standalone running
from abstract_filter import *
import math


class AlignedProportion(AbstractFilter):
	def __init__(self):
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

	#
	def initialize(self, source_language, target_language):
		self.num_of_scans = 1
		self.src_language = source_language
		self.trg_language = target_language

		return

	def finalize(self):
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

	#
	def process_tu(self, tu, num_of_finished_scans):
		src_set = set([x[0] for x in tu.alignment])
		trg_set = set([x[1] for x in tu.alignment])

		src_size = float(len(tu.src_tokens))
		trg_size = float(len(tu.trg_tokens))

		if src_size == 0 or trg_size == 0:
			return

		self.n += 1
		src_ratio = float(len(src_set)) / src_size
		trg_ratio = float(len(trg_set)) / trg_size

		self.src_sum += src_ratio
		self.src_sum_sq += src_ratio * src_ratio
		self.trg_sum += trg_ratio
		self.trg_sum_sq += trg_ratio * trg_ratio

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

		if src_ratio > 2 * self.src_var or trg_ratio > 2 * self.trg_var:
			return 'reject'
		return 'accept'
