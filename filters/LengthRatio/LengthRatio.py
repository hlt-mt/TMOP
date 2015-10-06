# sys.path.append(os.getcwd() + '/..') # Uncomment for standalone running
from abstract_filter import *
import math


class LengthRatio(AbstractFilter):
	def __init__(self):
		self.src_language = ""
		self.trg_language = ""

		self.n = 0.0
		self.sum = 0.0
		self.sum_sq = 0.0

		self.mean = 0.0
		self.var = 0.0

	def initialize(self, source_language, target_language):
		self.num_of_scans = 1
		self.src_language = source_language
		self.trg_language = target_language
		return

	def finalize(self):
		if self.n == 0:
			self.n += 1.0
		self.mean = self.sum / self.n
		self.var = (self.sum_sq - (self.sum * self.sum) / self.n) / (self.n - 1)
		self.var = math.sqrt(self.var)

	def process_tu(self, tu, num_of_finished_scans):
		ratio = len(tu.src_phrase) / max(len(tu.trg_phrase), 1.0)

		self.n += 1
		self.sum += ratio
		self.sum_sq += ratio * ratio

	def do_after_a_full_scan(self, num_of_finished_scans):
		return

	def decide(self, tu):
		ratio = len(tu.src_phrase) / max(len(tu.trg_phrase), 1.0)

		ratio -= self.mean
		ratio = math.fabs(ratio)

		if ratio <= 2 * self.var:
			return 'accept'
		return 'reject'
