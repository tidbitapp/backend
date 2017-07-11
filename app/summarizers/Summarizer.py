from . import Frequency
from . import Luhn
from . import SumBasic

SUMMARIZER_TYPES = ["FREQUENCY", "LUHN", "SUMBASIC"]

def summarize(text, summarizer_type):
  summary = ""
  if summarizer_type == SUMMARIZER_TYPES[0]: 	# Frequency summarizer
    summary = Frequency.freq_summarize(text, Frequency.NUM_SUMMARIZED_SENTENCES)
  elif summarizer_type == SUMMARIZER_TYPES[1]: 	# Luhn summarizer
    summary = Luhn.luhn_summarize(text, Luhn.NUM_SUMMARIZED_SENTENCES)
  elif summarizer_type == SUMMARIZER_TYPES[2]: 	# SumBasic summarizer
    summary = SumBasic.sumbasic_summarize(text, SumBasic.NUM_SUMMARIZED_SENTENCES)		
    
  return summary
  
