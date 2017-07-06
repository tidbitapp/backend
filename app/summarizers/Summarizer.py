from . import Frequency

SUMMARIZER_TYPES = ["FREQUENCY"]

def summarize(text, summarizer_type):
  summary = ""
  if summarizer_type == SUMMARIZER_TYPES[0]: 	# Frequency summarizer
    summary = Frequency.freq_summarize(text, Frequency.NUM_SUMMARIZED_SENTENCES)
		
  return summary
  
