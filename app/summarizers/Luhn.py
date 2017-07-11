from operator import itemgetter
import re
import sys
from . import utils

FILE_STOP_WORD_LIST = "stop-word-list.txt"
MIN_FREQ = 0.001
MAX_FREQ = 0.5
NUM_SUMMARIZED_SENTENCES = 3
MIN_SENTENCE_LENGTH = 5

# Returns the stop word list
def get_stop_word_list():
  l = []
    
  f = open("tidbit/app/summarizers/" + FILE_STOP_WORD_LIST)
  for word in f.read().split():
    l.append(word)

  f.close()

  return l
  
# Returns a list of the signifcant words extracted from the text
def get_significant_words(word_freq, stop_words):
  significant_words = []
  
  """ Remove all the words in the list that either are:
  - Stop words OR
  - Their frequency is below or above the min or max thresholds
  """
  for word, freq in word_freq.items():
    if word not in stop_words and freq > MIN_FREQ and freq < MAX_FREQ:
      significant_words.append(word)

  return significant_words

# Returns the score of a sentence
def calc_sentence_score(sentence, significant_words):
  if len(sentence.strip('.!?,()\n')) < MIN_SENTENCE_LENGTH:
    return 0.0

  num_important_words = 0
  max_dist = 0 # Maximum distance between two significant words
  pos_last_sign_word = 0
  curr_pos = 0

  for word in sentence.split():
    word = word.strip('.!?,()\n').lower()
    if word in significant_words:
      num_important_words += 1
      dist = curr_pos - pos_last_sign_word
      if dist > max_dist:
        max_dist  = dist    

    curr_pos += 1
  
  score = sys.float_info.max
  if max_dist > 0:
    score = float(num_important_words ** 2) / float(max_dist)

  return score
  

def luhn_summarize(text, num_summarized_sentences):
  stop_words = []
  sentences = []
  word_freq = {}
  significant_words = []

  # Get list of stop words
  stop_words = get_stop_word_list()
  # Split the text into sentences
  sentences = utils.split_into_sentences(text)
  # Calculate the word frequencies
  word_freq = utils.calc_word_freq(sentences)
  # Find the significant words in the text
  significant_words = get_significant_words(word_freq, stop_words)
 
  # Calc the score of every sentence and also note its overall position in the text
  scored_sentences = [(s, calc_sentence_score(s, significant_words), order) for order, s in enumerate(sentences)]

  # Sort by the ranking of the sentence
  ranked_sentences = sorted(scored_sentences, key=lambda x: x[1], reverse=True)
  # Grab the first NUM_SENTENCES highest ranked sentences
  ranked_sentences = ranked_sentences[0:num_summarized_sentences]
  # Sort the sentences by the order they appear in the text
  ranked_sentences = sorted(ranked_sentences, key=lambda x: x[2])


  return [s[0] for s in ranked_sentences]

	
