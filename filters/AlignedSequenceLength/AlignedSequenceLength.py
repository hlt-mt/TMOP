# sys.path.append(os.getcwd() + '/..') # Uncomment for standalone running
from abstract_filter import *
import math


class AlignedSequenceLength(AbstractFilter):
	def __init__(self):
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

	#
	def initialize(self, source_language, target_language):
		self.num_of_scans = 1
		self.src_language = source_language
		self.trg_language = target_language

		return

	def finalize(self):
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

	#
	def process_tu(self, tu, num_of_finished_scans):
		src_set = set([x[0] for x in tu.alignment])
		trg_set = set([x[1] for x in tu.alignment])
		src_size = float(len(tu.src_tokens))
		trg_size = float(len(tu.trg_tokens))

		if src_size == 0 or trg_size == 0:
			return

		src_bar = set([i for i in range(int(src_size))])
		trg_bar = set([i for i in range(int(trg_size))])
		src_set = src_bar - src_set
		trg_set = trg_bar - trg_set

		last = -1
		for current in src_set:
			if current - last > 1:
				self.src_n += 1
				self.src_sum += (current - last - 1)
				self.src_sum_sq += (current - last - 1) * (current - last - 1)
			last = current
		if src_size - last > 1:
			self.src_n += 1
			self.src_sum += (src_size - last - 1)
			self.src_sum_sq += (src_size - last - 1) * (src_size - last - 1)

		last = -1
		for current in trg_set:
			if current - last > 1:
				self.trg_n += 1
				self.trg_sum += (current - last - 1)
				self.trg_sum_sq += (current - last - 1) * (current - last - 1)
			last = current
		if trg_size - last > 1:
			self.trg_n += 1
			self.trg_sum += (trg_size - last - 1)
			self.trg_sum_sq += (trg_size - last - 1) * (trg_size - last - 1)


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

		src_mean = abs(src_mean - self.src_mean)
		trg_mean = abs(trg_mean - self.trg_mean)

		if src_mean > 2 * self.src_var or trg_mean > 2 * self.trg_var:
			return 'reject'
		return 'accept'
