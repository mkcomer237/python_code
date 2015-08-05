import sys
import json
import nltk

def getscores(textbody, scores):
	score = 0
	words = textbody.split()
	for word in words:
		try:
			score = score + scores[str(word)]
			print word, score
		except (IndexError, KeyError):
			pass
	return(score)


def load_sentiments(filepath):
  sentiments = open(filepath)
  scores = {} # initialize an empty dictionary
  for line in sentiments:
    term, score  = line.split("\t")  # The file is tab-delimited. "\t" means "tab character"
    scores[term] = int(score)  # Convert the score to an integer.
  return scores


conversations = open('test_conversations.txt')

for line in conversations:
  totalscore = 0
  splitline = line.split('\t')
  textbody = splitline[3].lower()
  
  scores = load_sentiments('AFINN-111.txt')
  

  totalscore_a = getscores(textbody, scores)
  
  print totalscore_a, line.strip()


 






