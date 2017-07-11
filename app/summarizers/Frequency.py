from operator import itemgetter
from . import utils

NUM_SUMMARIZED_SENTENCES = 3
MIN_SENTENCE_LENGTH = 5

def freq_summarize(text, num_summarized_sentences):
  word_freq = {}
  sentence_score = {}

  # Split the text into sentences
  sentences = utils.split_into_sentences(text)
  

  # Count the frequency of each word in the text
  word_freq = utils.calc_word_freq(sentences)

  order = 0
  # Calculate the rank of each sentence based on its words' frequencies
  for s in sentences:
    words = s.split()

    # Reject smaller sentence which probably don't have much info
    if len(words) < MIN_SENTENCE_LENGTH : continue

    # Store the relative order in which this sentence appears in the text
    sentence_score[s] = [0, order]
    for word in words:
      word = word.strip('.!?,()\n').lower()
      sentence_score[s][0] += word_freq[word]
    # Normalize the ranking of the sentence by dividing by its no. of words
    sentence_score[s][0] /= len(s)
    
    order += 1

  # Sort by the ranking of the sentence
  ranked_sentences = sorted(sentence_score.items(), key=lambda x: x[1][0], reverse=True)
  # Grab the first NUM_SENTENCES highest ranked sentences
  ranked_sentences = ranked_sentences[0:num_summarized_sentences]
  # Sort the sentences by the order they appear in the text
  ranked_sentences = sorted(ranked_sentences, key=lambda x: x[1][1])
   
  return [s[0] for s in ranked_sentences]
