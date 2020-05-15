# sys.path.append(os.getcwd() + '/..') # Uncomment for standalone running
from abstract_policy import *


class TwentyNo(AbstractPolicy):
	def __init__(self):
		print("TwentyNo ready")
		return

	def decide(self, result_list):
		num_of_no_answers = len([1 for x in result_list if x[1] == "reject"])
		if (float(num_of_no_answers)/float(len(result_list))) > 0.2:
			return 'reject'
		return 'accept'
