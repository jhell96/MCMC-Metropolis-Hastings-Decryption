"""
Author: Josh Hellerstein
Date: 1/4/2017
File: mcmc.py
"""
from __future__ import division
from util import Distribution
import string
import math
import random
import sys

import matplotlib.pyplot as plt

def build_letter_transition_dist(file):
	"""
	Builds a transition matrix (dict of dicts) which measures the probability of transitioning from 
	one letter to another letter, based on the frequencies from the sample file. 
	i.e. "Spam and Eggs" measures frequency of s->p, p->a, a->m, m->" ", " "->a, a->n etc...

	Inputs
	------
	file : a string which is the path to a file containing the reference document

	Returns
	-------
	a dictionary of Distribution objects (inherited from dict - see util) where each 
	key is a letter, and each key of each Distribution object is also a letter; the
	value is the probablity of transitioning between letters, 
	i.e. d[first_letter][second_letter] = Probability of first_letter -> second_letter	
	"""
	charset = string.lowercase+" "

	dist = {key:Distribution() for key in charset}
	
	doc = clean_document(open(file).read())
	
	# laplace smoothing - setting the prior to a uniform distribution.
	# avoids probabilites of 0 in the transition distirbution.
	for a in charset:
		for b in charset:
			dist[a][b] += 1

	for i in range(1, len(doc)):
		first_letter = doc[i-1] if doc[i-1].isalpha() else " "
		second_letter = doc[i] if doc[i].isalpha() else " "
		
		dist[first_letter][second_letter] +=1

	for k in dist:
		dist[k].renormalize()

	return dist

def plot_freq(dist):
	"""
	Plots the transition distribution created in build_letter_transition_dist -- for utility and visualization
	"""
	data = [ [dist[i][j] for j in dist[i]] for i in dist]
	charset = [i for i in dist]

	fig = plt.figure()
	ax = fig.add_subplot(111)

	ax.set_xlim((0, len(charset)-1))
	ax.set_ylim((0, len(charset)-1))

	ax.set_xticks([i for i in range(len(charset))])
	ax.set_xticklabels(charset)

	ax.set_yticks([i for i in range(len(charset))])
	ax.set_yticklabels(charset)

	plt.grid(True, color='white')
	plt.imshow(data)
	plt.colorbar(orientation='vertical')
	plt.show()

def clean_document(document):
	"""
	Removes punctuation from a document, and converts everything to lowercase
	"""
	return document.translate(None, string.punctuation).lower()

def compute_log_likelihood(document, expected_letter_distribution):
	"""
	Computes the log-likelihood of a document

	Inputs
	------
	document : a string, of which, we compute the likelihood

	expected_letter_distribution : a dictionary of Distribution objects (inherited from dict - see util) where each 
									key is a letter, and each key of each Distribution object is also a letter; the
									value is the probablity of transitioning between letters, 
									i.e. d[first_letter][second_letter] = Probability of first_letter -> second_letter

	Returns
	-------
	a double which is the log-likelihood of the document	
	"""
	s = 0

	for i in range(1, len(document)):
		first_letter = document[i-1].lower() if document[i-1].isalpha() else " "
		second_letter = document[i].lower() if document[i].isalpha() else " "
		s += math.log(expected_letter_distribution[first_letter][second_letter])

	return s

def decrypt_document(encrypted_document, cipher):
	"""
	Decrypts a document from a cipher

	Inputs
	------
	encrypted_document : a string, which we want to transform with a cipher

	cipher : a string, in which order matters, that is mapped to from the alphabet in the 
			 encrypted document i.e. abcdefg.. -> udhjenk...

	Returns
	-------
	a string in which each original letter, is replaced with its corresponding letter in the cipher
	"""
	mapping = create_mapping_from_cipher(cipher)
	document = ""
	for c in encrypted_document:
		if (c.isalpha() and (c.lower() in mapping)):
			document += mapping[c.lower()]
		else:
			document += " "

	return document

def create_mapping_from_cipher(cipher):
	"""
	Creates the mapping between the alphabet string and the cipher string

	Inputs
	------
	cipher : a string, in which order matters, that is mapped to from the alphabet in the 
			 encrypted document i.e. abcdefg.. -> udhjenk...

	Returns
	-------
	a dictionary in which each key is a letter of the alphabet, and each value is
	the corresponding letter in the cipher
	"""
	charset = list(string.lowercase)
	return {charset.pop(0):elem for elem in cipher}

def propose_cipher(current_cipher):
	"""
	Proposes a new cipher by randomly swapping the place of two letters in the current cipher

	Inputs
	------
	current_cipher : a string, in which order matters, that is mapped to from the alphabet in the 
			 		 encrypted document i.e. abcdefg.. -> udhjenk...

	Returns
	-------
	a string, which is the new proposed cipher
	"""
	first_letter = random.choice(list(current_cipher))
	second_letter = random.choice(list(current_cipher))

	while(first_letter == second_letter):
		second_letter = random.choice(list(current_cipher))

	new_cipher = ""
	for c in current_cipher:
		if (c == first_letter):
			new_cipher += second_letter
		elif (c == second_letter):
			new_cipher += first_letter
		else:
			new_cipher+=c

	return new_cipher

def generate_random_cipher():
	"""
	Generates a random cipher string

	Returns
	-------
	a string, containing all the letters of the alphabet, in a randomly permuated order
	"""
	current_cipher = list(string.lowercase)
	random.shuffle(current_cipher)
	return "".join(current_cipher) 

def acceptance_criteria(log_proposal, log_current):
	"""
	Accepts the sample according to the Metropolis-Hastings algorithm
	"""
	return (random.random() < math.exp(log_proposal - log_current))

def run_metropolis_hastings(encrypted_document, expected_letter_distribution, max_acceptance_iter=4000):
	"""
	Runs the Metropolis-Hastings algorithm to decode the document. The iteration number represents 
	the number of accepted samples from the distribution, and depends heavily on the length of the document
	to be decoded: A longer document usually implies smaller terminal iteration number. 

	If it doesn't decode the document the first time, it is often useful to run multiple times to yield the best
	cipher.
	"""
	encrypted_document = clean_document(encrypted_document)

	current_cipher = generate_random_cipher()

	best_document = ("", float("-inf"))

	number_accepted = 0
	i = 0

	while(number_accepted < max_acceptance_iter): 
		i+=1
		proposal_cipher = propose_cipher(current_cipher)

		proposal_document = decrypt_document(encrypted_document, proposal_cipher)
		current_document = decrypt_document(encrypted_document, current_cipher)

		log_likelihood_proposal = compute_log_likelihood(proposal_document, expected_letter_distribution)
		log_likelihood_current = compute_log_likelihood(current_document, expected_letter_distribution)


		if (log_likelihood_proposal > best_document[1]):
			best_document = (proposal_document, log_likelihood_proposal)

		if(acceptance_criteria(log_likelihood_proposal, log_likelihood_current)):
			number_accepted += 1
			current_cipher = proposal_cipher

		print number_accepted, i
		print best_document

	return best_document

def encrypt_document(document):
	"""
	Useful method to encrypt a document using a random cipher
	"""
	cipher = generate_random_cipher()
	return decrypt_document(document, cipher)

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print "Usage: python mcmc.py <path to file to decode> <number of iterations> <path to reference document>"
        print "Example: python mcmc.py decode_this.txt 2000 war_and_peace.txt"
        sys.exit(1)

    file_to_decode = open(sys.argv[1]).read()
    expected_letter_distribution = build_letter_transition_dist(sys.argv[3])
    iterations = int(sys.argv[2])

    print run_metropolis_hastings(file_to_decode, expected_letter_distribution, iterations)
