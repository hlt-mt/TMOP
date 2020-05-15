# sys.path.append(os.getcwd() + '/..') # Uncomment for standalone running
from abstract_policy import *


class OneNo(AbstractPolicy):
	def __init__(self):
		print("OneNo ready")
		return

	def decide(self, result_list):
		num_of_no_answers = len([1 for x in result_list if x[1] == "reject"])
		if num_of_no_answers > 0:
			return 'reject'
		return 'accept'
