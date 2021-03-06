"""
	This file is for constructing stimuli pairs
	
	A X B  <->  A Y B
	
	with the unigram and bigram stats matched
	
	It requires you to have run compute_trigram_stats and output the result to /ssd/trigram-stats
	It also takes a bad word file to filter out bad words from our experimental stimuli.
	
	This
"""

from ngrampy.LineFile import *
import os
SUBSAMPLE_N = 50000000
tolerance = 0.01
BAD_WORD_FILE = "badwords.txt"

def check_tolerance(x,y):
	"""
		A handy function to check if some variables are within tolerance percent of each other
	"""
	return abs(x-y) / ((x+y)/2.) < tolerance

# This will copy the file, make a new one, and then print out possible lines
G = LineFile(files=["/ssd/trigram-stats"], path="/ssd/subsampled-stimuli", header="w1 w2 w3 c123 c1 c2 c3 c12 c23 unigram bigram trigram")

# Now throw out the porno words
#porno_vocabulary = [ l.strip() for l in open(BAD_WORD_FILE, "r") ]
#G.restrict_vocabulary("w1 w2 w3", porno_vocabulary, invert=True)

# draw a subsample
#if SUBSAMPLE_N is not None:
	#G.subsample_lines(N=SUBSAMPLE_N)

# we need to resort  this so that we can have w1 and w3 equal and then all the n-grams matched
G.sort("w1 w3 unigram bigram trigram", lines=1000000)
G.head()

item_number = 0
line_stack = []
for l in G.lines(tmp=False, parts=False):
	# extract the columns from line
	w1, w3, unigram, bigram, trigram =  G.extract_columns(l, keys="w1 w3 unigram bigram trigram", dtype=[str, str, float, float, float])
	
	# now remove things which cannot possibly match anymore
	while len(line_stack) > 0:
		w1_, w3_, unigram_, bigram_, trigram =  G.extract_columns(line_stack[0], keys="w1 w3 unigram bigram trigram", dtype=[str, str, float, float, float])
		
		if not (w1_ == w1 and w3_ == w3 and check_tolerance(unigram, unigram_)):
			del line_stack[0]
			
	# now go through the line_stack and try out each 
	# it must already be within tolerance on unigram, or it would have been removed
	for x in line_stack:
		w1_, w3_, unigram_, bigram_, trigram =  G.extract_columns(x, keys="w1 w3 unigram bigram trigram", dtype=[str, str, float, float, float])
		
		# it must have already been within tolerance on unigram or it would be removed
		assert( check_tolerance(unigram, unigram_) ) 
		assert( w1_ == w1 and w3_ == w3 )
		
		# and check the bigrams
		if check_tolerance(bigram, bigram_) and (w1==w1_ and w3==w3_):
			print len(line_stack), item_number, l
			print len(line_stack), item_number, x
			item_number += 1
		
	# and add this on
	line_stack.append(l)
