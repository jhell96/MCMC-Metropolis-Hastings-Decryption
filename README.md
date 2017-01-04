# MCMC-Metropolis-Hastings-Decryption
Uses the Metropolis-Hastings algorithm to decode a simple substitution cipher on 26 lowercase characters of the alphabet.
Could potentially be used to decode cryptograms of medium length.

## Process and Comments:
- Builds a frequency distribution of letter-transitions from War and Peace.
- Explores 26! ciphers (permutations of the alphabet) using the Metropolis-Hastings algorithm greedily, by maximizing the log-likelihood of the document, based on the letter-transition distribution.
- Metropolis-Hastings avoids local maxima, and usually converges to the correct solution within 3000 "accepted samples." 
- A sample is accepted when:
```python
random.random() < math.exp(log_likelihood_proposal_cipher - log_likelihood_current_cipher)
```
- Longer coded documents tend to converge with less accepted samples.
- Only requires `matplotlib` for visualization -- can run with only standard python libraries.

## Usage:
- Format to run is: `python mcmc.py <path to file to decode> <number of iterations> <path to reference document>`
- Run the test file with the command `python mcmc.py decode_this.txt 1000 war_and_peace.txt`
- Change the number of iterations to reflect the length of the document you're trying to decode
- To encode a document for testing with a random cipher use `encrypt_document(document)`
- To visualize the letter-transitions from War and Peace use `plot_freq(build_letter_transition_dist(file))`

## References:
- 6.008 course at MIT
- [The Markov Chain Monte Carlo Revolution](http://statweb.stanford.edu/~cgates/PERSI/papers/MCMCRev.pdf) 

## License:
[Standard MIT License](../master/LICENSE)
