# sys.path.append(os.getcwd() + '/..') # Uncomment for standalone running
from abstract_filter import *
import re


class RepeatedWords(AbstractFilter):
	def __init__(self):
		self.num_of_scans = 0
		self.src_language = ""
		self.trg_language = ""

		self.repeated_chars_re = None

	#
	def initialize(self, source_language, target_language, extra_args):
		self.num_of_scans = 1
		self.src_language = extra_args['source language']
		self.trg_language = extra_args['target language']

		self.repeated_words_re = re.compile(r"\b(\w+)(\s+\1)+\b")
		return

	def finalize(self):
		pass

	def process_tu(self, tu, num_of_finished_scans):
		src_repeated_words = len(self.repeated_words_re.findall(tu.src_phrase))
		trg_repeated_words = len(self.repeated_words_re.findall(tu.trg_phrase))

		if src_repeated_words + trg_repeated_words > 0:
			return [0]
		return [1]

	def do_after_a_full_scan(self, num_of_finished_scans):
		pass

	def decide(self, tu):
		# - Repeated chars occurrence --------------------------------------------
		src_repeated_words = len(self.repeated_words_re.findall(tu.src_phrase))
		trg_repeated_words = len(self.repeated_words_re.findall(tu.trg_phrase))

		if src_repeated_words + trg_repeated_words > 0:
			return 'reject'
		return 'accept'
