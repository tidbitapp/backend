from operator import itemgetter
import re

NUM_SUMMARIZED_SENTENCES = 5
MIN_SENTENCE_LENGTH = 5
from . import utils

# Calculates the score, or rank, of the given sentence based on the
# frequency of its words
def calc_sentence_score(sentence, word_prob):
  if len(sentence.split()) < MIN_SENTENCE_LENGTH: return 0

  score = 0
  num_words = 0
  words = []

  words = sentence.split()
  num_words = len(words)
  for word in words:
    word = word.strip('.!?,()\n').lower()
    score += word_prob[word] / float(num_words)
    
  return score

# Returns the word in the dictionary with the highest frequency
def get_max_freq_word(word_prob):
  return max(word_prob, key=word_prob.get)

def sumbasic_summarize(text, num_summarized_sentences):
  sentences = []
  word_prob = {}
  summary_sentences = []

  # Split the text into sentences
  sentences = utils.split_into_sentences(text)

  if len(sentences) <= num_summarized_sentences:
    return sentences

  # Calculate the word frequencies (i.e. their probabilities)
  word_prob = utils.calc_word_freq(sentences)
  
  # Calc the score of every sentence and also note its overall position in 
  scored_sentences = [(s, calc_sentence_score(s, word_prob), order) for order, s in enumerate(sentences)]
  # Sort by the ranking of the sentence
  ranked_sentences = sorted(scored_sentences, key=lambda x: x[1], reverse=True)

  highest_freq_word = ""
  words = []
  while len(summary_sentences) < num_summarized_sentences:
    highest_freq_word = get_max_freq_word(word_prob)

    for s in ranked_sentences:
      words = [word.strip('.!?,()\n').lower() for word in s[0].split()]
      
      # Check that the max. freq. word is in the sentence
      if highest_freq_word in words:
        # If the sentence is already included in the summary, skip it
        if s in summary_sentences: continue
        # Otherwise, append the sentence to the summary
        summary_sentences.append(s)

        # Update the prob. of each word in the chosen sentence
        for word in words:
          word_prob[word] = word_prob[word] * word_prob[word]

        break

  # Sort the sentences by the order they appear in the text
  summary_sentences = sorted(summary_sentences, key=lambda x: x[2])

  return [s[0] for s in summary_sentences]
