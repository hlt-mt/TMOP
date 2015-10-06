# sys.path.append(os.getcwd() + '/..') # Uncomment for standalone running
from abstract_policy import *


class SingleFilterPolicy(AbstractPolicy):
	def __init__(self):
		print "SingleFilterPolicy ready"
		return

	def decide(self, result_list):
		return result_list[0][1]
