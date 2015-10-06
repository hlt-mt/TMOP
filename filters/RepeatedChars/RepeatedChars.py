# sys.path.append(os.getcwd() + '/..') # Uncomment for standalone running
from abstract_filter import *
import re


class RepeatedChars(AbstractFilter):
	def __init__(self):
		self.num_of_scans = 0
		self.src_language = ""
		self.trg_language = ""

		self.repeated_chars_re = None

	#
	def initialize(self, source_language, target_language):
		self.num_of_scans = 0
		self.src_language = source_language
		self.trg_language = target_language

		self.repeated_chars_re = re.compile(r"(\w)\1{2,}")
		return

	def finalize(self):
		pass

	def process_tu(self, tu, num_of_finished_scans):
		pass

	def do_after_a_full_scan(self, num_of_finished_scans):
		pass

	def decide(self, tu):
		minus_points = 0

		# - Repeated chars length ------------------------------------------------
		# src_repeated_chars = self.repeated_chars_re.finditer(tu.src_phrase)
		# trg_repeated_chars = self.repeated_chars_re.finditer(tu.trg_phrase)

		# src_max_length_of_repeat = max(0, [len(x.group(0)) for x in src_repeated_chars])
		# trg_max_length_of_repeat = max(0, [len(x.group(0)) for x in trg_repeated_chars])
		# if (src_max_length_of_repeat > 3 and trg_max_length_of_repeat <= 3) or (src_max_length_of_repeat < 3 and trg_max_length_of_repeat > 3):
			# minus_points += 1

		# - Repeated chars occurrence --------------------------------------------
		src_repeated_chars = len(self.repeated_chars_re.findall(tu.src_phrase))
		trg_repeated_chars = len(self.repeated_chars_re.findall(tu.trg_phrase))

		if src_repeated_chars != trg_repeated_chars:
			minus_points += 1

		if minus_points > 0:
			return 'reject'
		return 'accept'
