# sys.path.append(os.getcwd() + '/..') # Uncomment for standalone running
from abstract_filter import *
import math


class WordLength(AbstractFilter):
	def __init__(self):
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

	#
	def initialize(self, source_language, target_language):
		self.num_of_scans = 1
		self.src_language = source_language
		self.trg_language = target_language

		return

	def finalize(self):
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

	def process_tu(self, tu, num_of_finished_scans):
		for word in tu.src_tokens:
			self.src_n += 1
			self.src_sum += len(word)
			self.src_sum_sq += len(word) * len(word)

		for word in tu.trg_tokens:
			self.trg_n += 1
			self.trg_sum += len(word)
			self.trg_sum_sq += len(word) * len(word)

	def do_after_a_full_scan(self, num_of_finished_scans):
		pass

	def decide(self, tu):
		src_ool_words = 0  # Out of Length words
		trg_ool_words = 0  # Out of Length words

		for word in tu.src_tokens:
			tmp = len(word) - self.src_mean
			# tmp = math.fabs(tmp)

			if tmp > 3 * self.src_var:
				src_ool_words += 1
				# print word

		for word in tu.trg_tokens:
			tmp = len(word) - self.trg_mean
			# tmp = math.fabs(tmp)

			if tmp > 3 * self.trg_var:
				trg_ool_words += 1

		if src_ool_words > 0 or trg_ool_words > 0:
			return 'reject'
		return 'accept'
