# sys.path.append(os.getcwd() + '/..') # Uncomment for standalone running
from abstract_filter import *
from collections import Counter
from scipy.sparse import lil_matrix
from scipy.spatial.distance import cosine
from gensim.matutils import Sparse2Corpus
from gensim.models import lsimodel
from sets import Set
import numpy as np
import os.path
import math


class WE_ScoreAlign_BestForRest(AbstractFilter):
	def __init__(self):
		self.var_mult = 2.0

		self.src_language = ""
		self.trg_language = ""

		self.min_count = 3
		self.num_of_features = 100
		self.thresh = 0.80

		self.all_words = []
		self.vocab = None
		self.vectors = None
		self.number_of_tus = 0

		self.model_file_name = "models/vectors_"
		self.dict_file_name = "models/dict_"

		self.n = 0.0
		self.sum = 0.0
		self.sum_sq = 0.0

		self.mean = 0.0
		self.var = 0.0

		self.model_exist = False

	#
	def initialize(self, source_language, target_language, extra_args):
		self.num_of_scans = 3
		self.src_language = extra_args['source language']
		self.trg_language = extra_args['target language']
		self.normalize = extra_args['normalize scores']
		self.stat_filename = "models/WE_ScoreAlign_BestForRest.stats"
		if self.normalize:
			self.stat_filename += "_n"

		self.model_file_name += self.src_language + self.trg_language
		self.dict_file_name += self.src_language + self.trg_language

		if os.path.isfile(self.model_file_name):
			print("Loading from file ...")
			# Don't need to train vectors
			self.num_of_scans = 1

			lsi = lsimodel.LsiModel.load(self.model_file_name)
			self.vectors = lsi.projection.u

			self.all_words = {}
			f = open(self.dict_file_name, "rb")

			for l in f:
				l = l.strip().split("\t")

				self.all_words[l[0]] = int(l[1])
			f.close()

		if os.path.isfile(self.stat_filename):
			lang_pair = self.src_language + self.trg_language
			f = open(self.stat_filename, 'r')

			l = f.readline()
			while l:
				if lang_pair not in l:
					l = f.readline()
					continue

				# Found the statistics (Don't need to calculate statistics either)
				self.model_exist = True
				self.num_of_scans = 0

				l = f.readline().strip().split("\t")
				self.mean = float(l[1])
				self.var = float(l[2])

				break

			f.close()

		if extra_args['emit scores'] == True:
			self.num_of_scans = 1
		return

	def finalize(self):
		if self.model_exist:
			print("Loaded stats from the model file.")
			return
		elif self.num_of_scans == 1:
			print("Loaded the model from file.")

		if self.n <= 1:
			self.n = 2.0
		self.mean = self.sum / self.n
		self.var = (self.sum_sq - (self.sum * self.sum) / self.n) / (self.n - 1)
		self.var = math.sqrt(self.var)

		f = open(self.stat_filename, 'a')
		lang_pair = self.src_language + self.trg_language
		f.write("\n" + lang_pair + "\n")
		f.write("stats\t" + str(self.mean) + "\t" + str(self.var) + "\n")
		f.close()

	def process_tu(self, tu, num_of_finished_scans):
		# The iteration before the last one (calculates the mean and variance based on the vectors)
		if (num_of_finished_scans == 0 and self.num_of_scans == 1) or num_of_finished_scans == 2:
			if len(tu.src_phrase) == 0 or len(tu.trg_phrase) == 0:
				return [0]

			index = -1
			src_vectors = {}
			for i, w in enumerate(tu.src_tokens):
				if w in self.all_words:
					index = self.all_words[w]
					src_vectors[i] = self.vectors[index]
			if index == -1:
				return [0]

			index = -1
			trg_vectors = {}
			for i, w in enumerate(tu.trg_tokens):
				if w in self.all_words:
					index = self.all_words[w]
					trg_vectors[i] = self.vectors[index]
			if index == -1:
				return [0]

			trg_mark = Set()
			avg_distance = 0.0
			counter = 0.0
			for align_pair in tu.alignment:
				s_w = align_pair[0]
				t_w = align_pair[1]

				if s_w in src_vectors and t_w in trg_vectors:
					dist = cosine(src_vectors[s_w], trg_vectors[t_w])
					trg_mark.add(t_w)
				else:
					continue

				avg_distance += dist
				counter += 1

			trg_mark = Set(trg_vectors) - trg_mark
			for t_w in trg_mark:
				min_dist = 1.0
				for s_w in src_vectors:
					dist = cosine(src_vectors[s_w], trg_vectors[t_w])
					min_dist = min(min_dist, dist)

				avg_distance += min_dist
				counter += 1

			if counter == 0:
				return [0]
			avg_distance /= counter

			self.n += 1
			self.sum += avg_distance
			self.sum_sq += avg_distance * avg_distance

			return [avg_distance]

		# First iteration of a normal run (collecting the vocabulary)
		elif num_of_finished_scans == 0:
			self.all_words += tu.src_tokens
			self.all_words += tu.trg_tokens
			self.number_of_tus += 1
		# Second iteration of a normal run (making the tu-word matrix)
		else:
			for w in tu.src_tokens + tu.trg_tokens:
				if w in self.all_words:
					self.vectors[self.all_words[w], self.number_of_tus] = 1

			self.number_of_tus += 1

	def do_after_a_full_scan(self, num_of_finished_scans):
		# First iteration of a normal run (collecting the vocabulary)
		if num_of_finished_scans == 1 and self.num_of_scans == 3:
			self.vocab = Counter(self.all_words)

			self.all_words = {}
			for word in self.vocab:
				if self.vocab[word] >= self.min_count:
					self.all_words[word] = len(self.all_words)

			self.vectors = lil_matrix((len(self.all_words), self.number_of_tus), dtype=np.int8)

			print("-#-#-#-#-#-#-#-#-#-#-#-")
			print("size of vocab:", len(self.vocab))
			print("size of common words:", len(self.all_words))
			print("number of TUs:", self.number_of_tus)
			self.number_of_tus = 0

			f = open(self.dict_file_name, "wb")

			for w in self.all_words:
				f.write(w.encode("utf-8"))
				f.write("\t" + str(self.all_words[w]) + "\n")
			f.close()

		# Second iteration of a normal run (making the tu-word matrix)
		elif num_of_finished_scans == 2:
			print("Performing SVD...")

			x = Sparse2Corpus(self.vectors)
			lsi = lsimodel.LsiModel(corpus=x, id2word=None, num_topics=self.num_of_features)
			lsi.save(self.model_file_name)
			self.vectors = lsi.projection.u

			print("done.")
		else:
			print("-#-#-#-#-#-#-#-#-#-#-#-")

	#
	def decide(self, tu):
		if len(tu.src_phrase) == 0 or len(tu.trg_phrase) == 0:
			return 'reject'

		index = -1
		src_vectors = {}
		for i, w in enumerate(tu.src_tokens):
			if w in self.all_words:
				index = self.all_words[w]
				src_vectors[i] = self.vectors[index]

		if index == -1:
			return 'neutral'

		index = -1
		trg_vectors = {}
		for i, w in enumerate(tu.trg_tokens):
			if w in self.all_words:
				index = self.all_words[w]
				trg_vectors[i] = self.vectors[index]

		if index == -1:
			return 'neutral'

		trg_mark = Set()
		avg_distance = 0.0
		counter = 0.0
		for align_pair in tu.alignment:
			s_w = align_pair[0]
			t_w = align_pair[1]

			if s_w in src_vectors and t_w in trg_vectors:
				dist = cosine(src_vectors[s_w], trg_vectors[t_w])
				trg_mark.add(t_w)
			else:
				continue

			avg_distance += dist
			counter += 1

		trg_mark = Set(trg_vectors) - trg_mark
		for t_w in trg_mark:
			min_dist = 1.0
			for s_w in src_vectors:
				dist = cosine(src_vectors[s_w], trg_vectors[t_w])
				min_dist = min(min_dist, dist)

			avg_distance += min_dist
			counter += 1

		if counter == 0:
			return 'neutral'
		avg_distance /= counter

		avg_distance -= self.mean
		avg_distance = math.fabs(avg_distance)

		if avg_distance <= self.var_mult * self.var:
			return 'accept'
		return 'reject'
