# sys.path.append(os.getcwd() + '/..') # Uncomment for standalone running
from abstract_filter import *
import math


class LengthStats(AbstractFilter):
	def __init__(self):
		self.src_language = ""
		self.trg_language = ""

		self.n = 0.0
		self.src_sum = 0.0
		self.trg_sum = 0.0
		self.src_wsum = 0.0
		self.trg_wsum = 0.0

		self.src_mean = 0.0
		self.trg_mean = 0.0

	def initialize(self, source_language, target_language, extra_args):
		self.num_of_scans = 1
		self.src_language = extra_args['source language']
		self.trg_language = extra_args['target language']
		self.normalize = extra_args['normalize scores']
		return

	def finalize(self):
		if self.n == 0:
			self.n += 1.0
		self.src_mean = self.src_sum / self.n
		self.trg_mean = self.trg_sum / self.n

		print 'src length mean:', self.src_mean
		print 'trg length mean:', self.trg_mean
		print 'src word mean:', self.src_wsum / self.n
		print 'trg word mean:', self.trg_wsum / self.n

	def process_tu(self, tu, num_of_finished_scans):
		self.src_wsum += len(tu.src_tokens)
		self.trg_wsum += len(tu.trg_tokens)
		self.src_sum += len(tu.src_phrase)
		self.trg_sum += len(tu.trg_phrase)
		self.n += 1

		return None

	def do_after_a_full_scan(self, num_of_finished_scans):
		return

	def decide(self, tu):
		return 'neutral'
