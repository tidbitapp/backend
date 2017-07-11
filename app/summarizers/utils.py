import re

# The code for this function was made by D Greenberg and can be found at:
# https://stackoverflow.com/questions/4576077/python-split-text-on-sentences
def split_into_sentences(text):
  caps = "([A-Z])"
  prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
  suffixes = "(Inc|Ltd|Jr|Sr|Co|Corp)"
  starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
  acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
  websites = "[.](com|net|org|io|gov)"

  text = " " + text + "  "
  text = text.replace("\n"," ")
  text = re.sub(prefixes,"\\1<prd>",text)
  text = re.sub(websites,"<prd>\\1",text)
  if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
  text = re.sub("\s" + caps + "[.] "," \\1<prd> ",text)
  text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
  text = re.sub(caps + "[.]" + caps + "[.]" + caps + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
  text = re.sub(caps + "[.]" + caps + "[.]","\\1<prd>\\2<prd>",text)
  text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
  text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
  text = re.sub(" " + caps + "[.]"," \\1<prd>",text)
  if "”" in text: text = text.replace(".”","”.")
  if "\"" in text: text = text.replace(".\"","\".")
  if "!" in text: text = text.replace("!\"","\"!")
  if "?" in text: text = text.replace("?\"","\"?")
  text = text.replace(".",".<stop>")
  text = text.replace("?","?<stop>")
  text = text.replace("!","!<stop>")
  text = text.replace("<prd>",".")
  sentences = text.split("<stop>")
  sentences = sentences[:-1]
  sentences = [s.strip() for s in sentences]
  return sentences
  
# Returns a dict with every word in the text and its relative frequency
def calc_word_freq(sentences):
  word_count = {}
  total_words = 0
  word_freq = {}

  # Count the number of times each word appears in the text
  for s in sentences:
    for word in s.split():
      word = word.strip('.!?,()\n').lower()
      if word not in word_count:
        word_count[word] = 1
      else:
        word_count[word] += 1
      total_words += 1

  # Calculate the frequency of each word
  for word, count in word_count.items():
    word_freq[word] = count / total_words

  return word_freq
