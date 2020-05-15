from abc import *
from copy import copy
"""
TMoP - Translation Memory Open-Source Purifier by Matteo Negri, Masoud Jalili Sabet and Marco Turchi, October 2015

Based on research by Matteo Negri, Masoud Jalili Sabet and Marco Turchi.

Copyright 2015 Matteo Negri, Masoud Jalili Sabet and Marco Turchi.  <negri@fbk.eu>, <jalili.masoud@gmail.com> and <turchi@fbk.eu>. All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are
permitted provided that the following conditions are met:

   1. Redistributions of source code must retain the above copyright notice, this list of
      conditions and the following disclaimer.

   2. Redistributions in binary form must reproduce the above copyright notice, this list
      of conditions and the following disclaimer in the documentation and/or other materials
      provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER ``AS IS'' AND ANY EXPRESS OR IMPLIED
WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those of the
authors and should not be interpreted as representing official policies, either expressed
or implied, of the copyright holder.
"""

class TU(object):
	# src_language = ""
	# trg_language = ""

	def __init__(self):
		self.src_phrase = ""
		self.trg_phrase = ""

		self.src_tokens = []
		self.trg_tokens = []

		self.alignment = []


def pass_by_value_decorator(old_f):
	def new_f(self, *l):
		new_l = [copy(element) for element in l]
		return old_f(self, *new_l)
	return new_f


class AbstractFilter(ABC):
	"""
	Basic Interface of a filter.
	This is an Abstract Base Class.
	"""

	# The number of scans required for the learning process.
	# It should be defined in the initialize() function and changing the value after the initialization has no effect.
	num_of_scans = 0

	def __init__(self):
		"""
		"""
		pass

	@abstractmethod
	def initialize(self, source_language, target_language):
		"""
		This function is called at the start of learning process (before the scans).
		It is the first function to initialize the calculations and prepare everything for the learning process.
		The num_of_scans variable should be initialized in this function.
		changing the value after the initialization has no effect.

		@type source_language: str
		@param source_language: The language of the first phrase in every translation unit.

		@type target_language: str
		@param target_language: The language of the second phrase in every translation unit.
		"""
		pass

	@abstractmethod
	def finalize(self):
		"""
		This function is called at the end of learning process (after all of the scans).
		It is the last function to finalize the calculations and prepare everything for the decision process.
		"""
		pass

	@abstractmethod
	def process_tu(self, tu, num_of_finished_scans):
		"""
		In every scan, for each translation unit this function is called.

		@type num_of_finished_scans: int
		@param num_of_finished_scans: The number of scans through the dataset that are finished until now.

		@type tu: TU
		@param tu: A Translation Unit with the source and the target phrase
		"""
		pass

	@abstractmethod
	def do_after_a_full_scan(self, num_of_finished_scans):
		"""
		After each scan through the dataset of TMs, this function will be called.
		It could be used to finalize the calculation after each scan.
		After the first scan the value of 'num_of_finished_scans' is 1.

		@type num_of_finished_scans: int
		@param num_of_finished_scans: The number of scans through the dataset that are finished until now.
		"""
		pass

	@abstractmethod
	def decide(self, tu):
		"""
		In the decision process this function is called for each translation unit.
		it should return 'accept', 'reject' or 'neutral'.

		@type tu: TU
		@param tu: A Translation Unit with the source and the target phrase

		@rtype: str
		@return: returns the decision from 'accept', 'reject' and 'neutral'.
		"""

		return 'accept'
