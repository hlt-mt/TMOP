from abc import *


class AbstractPolicy:
	"""
	Basic Interface of a decision policy.
	This is an Abstract Base Class.
	"""
	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self):
		"""
		"""
		pass

	@abstractmethod
	def decide(self, result_list):
		"""
		In the decision process this function is called for each translation unit.
		The input is a list of answers from all the filters.
		The output is a string and it could be one of the values 'accept', 'reject', 'neutral' or any arbitrary string.
		For each output string a file is created and the TUs with that result are appended to that file.

		@type result_list: list
		@param result_list: list of answers from all filters.

		@rtype: str
		@return: returns the decision from one of the values 'accept', 'reject', 'neutral' or any arbitrary string.
		"""

		return 'accept'
