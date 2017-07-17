import urllib.request
import freq_summarizer
from bs4 import BeautifulSoup

url = "https://www.bloomberg.com/news/articles/2017-06-25/takata-seeks-u-s-bankruptcy-protection-after-air-bag-recalls"
with urllib.request.urlopen(url) as content:
    html = content.read()

soup = BeautifulSoup(html)

# kill all script and style elements
for script in soup(["script", "style"]):
    script.extract()    # rip it out

# get text
text = soup.get_text()

# break into lines and remove leading and trailing space on each
lines = (line.strip() for line in text.splitlines())
# break multi-headlines into a line each
chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
# drop blank lines
text = '\n'.join(chunk for chunk in chunks if chunk)

print(freq_summarizer.freq_summarize(text))
