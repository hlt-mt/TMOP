# sys.path.append(os.getcwd() + '/..') # Uncomment for standalone running
from abstract_filter import *
from collections import Counter
from scipy.sparse import lil_matrix
from scipy.spatial.distance import cosine
import numpy as np
import random
import os.path
# from sklearn.decomposition import TruncatedSVD as SVD
from gensim.matutils import Sparse2Corpus
from gensim.models import lsimodel


class InvertedCentroidVector(AbstractFilter):
	def __init__(self):
		self.src_language = ""
		self.trg_language = ""

		self.min_count = 5
		self.num_of_features = 100
		self.thresh = 0.8

		self.all_words = []
		self.vocab = None
		self.vectors = None
		self.number_of_tus = 0

	def initialize(self, source_language, target_language):
		self.num_of_scans = 2
		self.src_language = source_language
		self.trg_language = target_language

		model_file = 'output/vectors_model_' + str(self.num_of_features)
		if os.path.isfile(model_file):
			self.num_of_scans = 0

			lsi = lsimodel.LsiModel.load(model_file)
			self.vectors = lsi.projection.u

	def finalize(self):
		if self.num_of_scans == 0:
			return

		print "Performing SVD..."

		# svd = SVD(n_components=self.num_of_features, random_state=42)
		# x = svd.fit_transform(self.vectors)
		# self.vectors = x

		x = Sparse2Corpus(self.vectors)
		lsi = lsimodel.LsiModel(corpus=x, id2word=None, num_topics=self.num_of_features)
		lsi.save('output/vectors_model_' + str(self.num_of_features))
		self.vectors = lsi.projection.u

		print "done."

	def process_tu(self, tu, num_of_finished_scans):
		if num_of_finished_scans == 0:
			self.all_words += tu.src_tokens
			self.all_words += tu.trg_tokens
			self.number_of_tus += 1
		else:
			for w in tu.src_tokens + tu.trg_tokens:
				if w in self.all_words:
					self.vectors[self.all_words.index(w), self.number_of_tus] += 1

			self.number_of_tus += 1

	def do_after_a_full_scan(self, num_of_finished_scans):
		if num_of_finished_scans == 1:
			self.vocab = Counter(self.all_words)

			self.all_words = []
			for word in self.vocab:
				if self.vocab[word] >= self.min_count:
					self.all_words.append(word)

			self.vectors = lil_matrix((len(self.all_words), self.number_of_tus), dtype=np.int8)

			print "-#-#-#-#-#-#-#-#-#-#-#-"
			print "size of vocab:", len(self.vocab)
			print "size of common words:", len(self.all_words)
			print "number of TUs:", self.number_of_tus
			self.number_of_tus = 0
		else:
			print "-#-#-#-#-#-#-#-#-#-#-#-"

	#
	def decide(self, tu):
		if len(tu.src_phrase) == 0 or len(tu.trg_phrase) == 0:
			return 'reject'

		src_vectors = []
		for w in tu.src_tokens:
			if w in self.all_words:
				index = self.all_words.index(w)
				src_vectors.append(self.vectors[index])

		if len(src_vectors) == 0:
			return 'neutral'
		src_rep = np.sum(src_vectors, axis=0)

		trg_vectors = []
		for w in tu.trg_tokens:
			if w in self.all_words:
				index = self.all_words.index(w)
				trg_vectors.append(self.vectors[index])

		if len(trg_vectors) == 0:
			return 'neutral'
		trg_rep = np.sum(trg_vectors, axis=0)

		distance = cosine(src_rep, trg_rep)
		if distance < self.thresh:
			return 'accept'
		return 'reject'
