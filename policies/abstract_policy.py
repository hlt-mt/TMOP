from abc import *
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

class AbstractPolicy(ABC):
	"""
	Basic Interface of a decision policy.
	This is an Abstract Base Class.
	"""

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
