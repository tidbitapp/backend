import re
from operator import itemgetter

NUM_SENTENCES = 3
MIN_SENTENCE_LENGTH = 5

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

def freq_summarize(text):
    word_count = {}
    total_words = 0
    word_freq = {}
    sentence_score = {}

    # Split the text into sentences
    sentences = split_into_sentences(text)

    # Count the number of times each word appears in the text
    for s in sentences:
        for word in s.split():
            if word not in word_count:
                word_count[word] = 1
            else:
                word_count[word] += 1
            total_words += 1

    # Calculate the frequency of each word
    for word, count in word_count.items():
        word_freq[word] = count / total_words

    order = 0
    # Calcula the rank of each sentence based on its words' frequencies
    for s in sentences:
        words = s.split()

        # Reject smaller sentence which probably don't have much info
        if len(words) < MIN_SENTENCE_LENGTH : continue

        # Store the relative order in which this sentence appears in the text
        sentence_score[s] = [0, order]
        for word in words:
            sentence_score[s][0] += word_freq[word]
        # Normalize the ranking of the sentence by dividing by its no. of words
        sentence_score[s][0] /= len(s)
        
        order += 1

    # Sort by the ranking of the sentence
    ranked_sentences = sorted(sentence_score.items(), key=lambda x: x[1][0], reverse=True)
    # Grab the first NUM_SENTENCES highest ranked sentences
    ranked_sentences = ranked_sentences[0:NUM_SENTENCES]
    # Sort the sentences by the order they appear in the text
    ranked_sentences = sorted(ranked_sentences, key=lambda x: x[1][1])
   
    return [s[0] for s in ranked_sentences]
    

f = open("article.txt", "r+")
text = f.read()

summary = freq_summarize(text)
for sentence in summary:
    print("- " + sentence + "\n")

