# sys.path.append(os.getcwd() + '/..') # Uncomment for standalone running
from abstract_filter import *
import re


class TagFinder(AbstractFilter):
	def __init__(self):
		self.num_of_scans = 0
		self.src_language = ""
		self.trg_language = ""

		self.date_re = None
		self.num_re = None
		self.url_re = None
		self.xml_re = None
		self.ref_re = None
		self.email_re = None
		self.image_re = None
		self.category_re = None
		return

#
	def initialize(self, source_language, target_language, extra_args):
		self.num_of_scans = 1
		self.src_language = extra_args['source language']
		self.trg_language = extra_args['target language']

		# ------------------------------------------------------------------------
		date_regex = r"(?:(?:31(\/|-|\.)(?:0?[13578]|1[02]|(?:Jan|Mar|May|Jul|Aug|Oct|Dec)))\1|" \
			r"(?:(?:29|30)(\/|-|\.)(?:0?[1,3-9]|1[0-2]|(?:Jan|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec))\2))" \
			r"(?:(?:1[0-9]|[2-9]\d)?\d{2})|(?:29(\/|-|\.)(?:0?2|(?:Feb))\3" \
			r"(?:(?:(?:1[0-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00))))" \
			r"|(?:0?[1-9]|1\d|2[0-8])(\/|-|\.)(?:(?:0?[1-9]|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep))" \
			r"|(?:1[0-2]|(?:Oct|Nov|Dec)))\4(?:(?:1[0-9]|[2-9]\d)?\d{2})"
		self.date_re = re.compile(date_regex)

		# ------------------------------------------------------------------------
		self.num_re = re.compile(r"\d+\.?\d*")

		# ------------------------------------------------------------------------
		self.ref_re = re.compile(r"<ref[^<]*<\/ref>")

		# ------------------------------------------------------------------------
		self.xml_re = re.compile(r"<[^>]*>")

		# ------------------------------------------------------------------------
		self.email_re = re.compile(r"[a-z0-9_\.-]+@[\da-z\.-]+\.[a-z\.]{2,6}")

		# ------------------------------------------------------------------------
		self.url_re = re.compile(r"(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w_\.-]+)*\/?")

		# ------------------------------------------------------------------------
		self.image_re = re.compile(r"\[\[image:[^\[\]]*\||\|\d+px|\|left|\|right|\|thumb")

		# ------------------------------------------------------------------------
		self.category_re = re.compile(r"\[\[category:([^|\]]*)[^]]*\]\]")

		return

	def finalize(self):
		pass

	def process_tu(self, tu, num_of_finished_scans):
		minus_points = 0

		# - Dates ----------------------------------------------------------------
		src_dates = len(self.date_re.findall(tu.src_phrase))
		trg_dates = len(self.date_re.findall(tu.trg_phrase))
		if src_dates != trg_dates:
			minus_points += 1
			# print "date"

		tu.src_phrase = self.date_re.sub("", tu.src_phrase)
		tu.trg_phrase = self.date_re.sub("", tu.trg_phrase)

		# - Numbers --------------------------------------------------------------
		src_nums = len(self.num_re.findall(tu.src_phrase))
		trg_nums = len(self.num_re.findall(tu.trg_phrase))
		if src_nums != trg_nums:
			minus_points += 1
			# print "num"
			# print tu.src_phrase
			# print tu.trg_phrase

		# - Reference tags -------------------------------------------------------
		src_ref = len(self.ref_re.findall(tu.src_phrase))
		trg_ref = len(self.ref_re.findall(tu.trg_phrase))
		if src_ref != trg_ref:
			minus_points += 1
			# print "ref"

		tu.src_phrase = self.ref_re.sub("", tu.src_phrase)
		tu.trg_phrase = self.ref_re.sub("", tu.trg_phrase)

		# - XML tags -------------------------------------------------------------
		src_xml_tag = len(self.xml_re.findall(tu.src_phrase))
		trg_xml_tag = len(self.xml_re.findall(tu.trg_phrase))
		if src_xml_tag != trg_xml_tag:
			minus_points += 1
			# print "xml"

		# - Emails ---------------------------------------------------------------
		src_emails = len(self.email_re.findall(tu.src_phrase))
		trg_emails = len(self.email_re.findall(tu.trg_phrase))
		if src_emails != trg_emails:
			minus_points += 1
			# print "email"

		# - URLs -----------------------------------------------------------------
		src_urls = len(self.url_re.findall(tu.src_phrase))
		trg_urls = len(self.url_re.findall(tu.trg_phrase))
		if src_urls != trg_urls:
			minus_points += 1
			# print "url"

		# - Image tags -----------------------------------------------------------
		src_img_tag = len(self.image_re.findall(tu.src_phrase))
		trg_img_tag = len(self.image_re.findall(tu.trg_phrase))
		if src_img_tag != trg_img_tag:
			minus_points += 1
			# print "img"

		# - Category tags --------------------------------------------------------
		src_cat_tag = len(self.category_re.findall(tu.src_phrase))
		trg_cat_tag = len(self.category_re.findall(tu.trg_phrase))
		if src_cat_tag != trg_cat_tag:
			minus_points += 1
			# print "cat"

		if minus_points > 1:
			return [0]
		return [1]

	def do_after_a_full_scan(self, num_of_finished_scans):
		pass

	def decide(self, tu):
		minus_points = 0

		# - Dates ----------------------------------------------------------------
		src_dates = len(self.date_re.findall(tu.src_phrase))
		trg_dates = len(self.date_re.findall(tu.trg_phrase))
		if src_dates != trg_dates:
			minus_points += 1
			# print "date"

		tu.src_phrase = self.date_re.sub("", tu.src_phrase)
		tu.trg_phrase = self.date_re.sub("", tu.trg_phrase)

		# - Numbers --------------------------------------------------------------
		src_nums = len(self.num_re.findall(tu.src_phrase))
		trg_nums = len(self.num_re.findall(tu.trg_phrase))
		if src_nums != trg_nums:
			minus_points += 1
			# print "num"
			# print tu.src_phrase
			# print tu.trg_phrase

		# - Reference tags -------------------------------------------------------
		src_ref = len(self.ref_re.findall(tu.src_phrase))
		trg_ref = len(self.ref_re.findall(tu.trg_phrase))
		if src_ref != trg_ref:
			minus_points += 1
			# print "ref"

		tu.src_phrase = self.ref_re.sub("", tu.src_phrase)
		tu.trg_phrase = self.ref_re.sub("", tu.trg_phrase)

		# - XML tags -------------------------------------------------------------
		src_xml_tag = len(self.xml_re.findall(tu.src_phrase))
		trg_xml_tag = len(self.xml_re.findall(tu.trg_phrase))
		if src_xml_tag != trg_xml_tag:
			minus_points += 1
			# print "xml"

		# - Emails ---------------------------------------------------------------
		src_emails = len(self.email_re.findall(tu.src_phrase))
		trg_emails = len(self.email_re.findall(tu.trg_phrase))
		if src_emails != trg_emails:
			minus_points += 1
			# print "email"

		# - URLs -----------------------------------------------------------------
		src_urls = len(self.url_re.findall(tu.src_phrase))
		trg_urls = len(self.url_re.findall(tu.trg_phrase))
		if src_urls != trg_urls:
			minus_points += 1
			# print "url"

		# - Image tags -----------------------------------------------------------
		src_img_tag = len(self.image_re.findall(tu.src_phrase))
		trg_img_tag = len(self.image_re.findall(tu.trg_phrase))
		if src_img_tag != trg_img_tag:
			minus_points += 1
			# print "img"

		# - Category tags --------------------------------------------------------
		src_cat_tag = len(self.category_re.findall(tu.src_phrase))
		trg_cat_tag = len(self.category_re.findall(tu.trg_phrase))
		if src_cat_tag != trg_cat_tag:
			minus_points += 1
			# print "cat"

		if src_cat_tag > 0:
			print "category tag -> edit them"
			print src_cat_tag
		if trg_cat_tag > 0:
			print "category tag -> edit them"
			print trg_cat_tag

		# ------------------------------------------------------------------------
		# ------------------------------------------------------------------------

		if minus_points > 1:
			return 'reject'
		return 'accept'
