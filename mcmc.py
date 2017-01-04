from __future__ import division
from util import Distribution
import string
import math
import random

import matplotlib.pyplot as plt

def build_letter_transition_dist(file):
	charset = string.lowercase+" "

	dist = {key:Distribution() for key in charset}
	
	doc = clean_document(open(file).read())
	
	#laplace smoothing, setting the prior to uniform distribution
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
	return document.translate(None, string.punctuation).lower()

def compute_log_likelihood(document, expected_letter_distribution):
	"""
	Inputs
	------
	document : a string to compute the likelihood of

	expected_letter_distribution : a 

	Returns
	-------
	
	"""
	s = 0
	for i in range(1, len(document)):
		first_letter = document[i-1] if document[i-1].isalpha() else " "
		second_letter = document[i] if document[i].isalpha() else " "
		s += math.log(expected_letter_distribution[first_letter][second_letter])

	return s

def decrypt_document(encrypted_document, cipher):
	mapping = create_mapping_from_cipher(cipher)
	document = ""
	for c in encrypted_document:
		if (c.isalpha() and (c.lower() in mapping)):
			document += mapping[c.lower()]
		else:
			document += " "

	return document

def create_mapping_from_cipher(cipher):
	charset = list(string.lowercase)
	return {charset.pop(0):elem for elem in cipher}

def propose_cipher(current_cipher):
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
	current_cipher = string.lowercase
	random.shuffle(list(current_cipher))
	return "".join(current_cipher) 

def acceptance_criteria(log_proposal, log_current):
	return (random.random() < math.exp(log_proposal - log_current))

def run_metropolis_hastings(encrypted_document, expected_letter_distribution):
	encrypted_document = clean_document(encrypted_document)

	current_cipher = generate_random_cipher()

	best_document = ("", float("-inf"))

	number_accepted = 0
	i = 0

	max_acceptance_iter = 8000

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

		print number_accepted, i, best_document

	return best_document

def encrypt_text(document):
	cipher = generate_random_cipher()
	return decrypt_document(document, cipher)

# plot_freq(build_letter_transition_dist("../war_and_peace.txt"))
text = "athzq qzmtby du ux kyvv cduwxuyc mxkzbcu maxuy kax zby dq dqmybyumdqi udmtzmdxqu mazm z lxtqi wybuxq kax ydmayb hzbbdyu xb cdyu du utby xp fydqi ndqcvl uwxnyq xp"
text2 = "txpub rezeh xjddj lepdg cpjrj edgbc dlztx jgrzs oepss txjtx zetpd jttxp pedbm siuup rtxpf sptmb rtxjt djfyr pjqtb sppju jeypx pjdpd tlpet fzejc cjedy rjerb dpjub ehtxp ueprv bislz txpag ztpup ettxz sljst xpmzr sttzu pxpxj dyppe dppup dbcdp ebihx tbhbl ztxxz scbrd mjtxp rjedx zsyrb txprs tbspp txpqz ehswi stzgp dbepz tljst xpeze txfpj rbmsi uuprj edtxp spvpe txbmy rjesc zmptx pujex jdypp etjqp ebits zdpjs ujccx bcdmj stzet xpxzc csrby ytxbi hxtxp ljsjl zcdcz ehxzs slbrd slbre tbuje gprjf dprtx pqzeh ypfbe dtxpl jcczt ujdpy rjess qzeor zgqcp tbtxz eqbmz txprp upuyp rpdtx pxpjr txtjc psbcd ejetb cdtxp utxpl zcdcz ehslp rpgri pcupe sxpsj zdscj vprsj edscj fprsj edtxz pvps"
text3 = encrypt_text(open("example.txt").read())
text4 = " TISTL HADRTS HAD SO PT OL IOS SO PT SHAS ME SHT BUTESMOI WHTSHTL SME IOPRTL "
text5 = "czonk o gosk ovt? zt gikn zieea gpet nzonk oxx jeog ws o uoa czon zwk apinz nppb o atoe np zpxu"
text6 = "ojkwk xt lnojxlz fnwk ylkdyqr ojql ojk kdyqr owkqofklo ns ylkdyqr gkngrk"
run_metropolis_hastings(text, build_letter_transition_dist("war_and_peace.txt"))
# print compute_log_likelihood("abd abd abd abd", build_letter_transition_dist("../war_and_peace.txt"))