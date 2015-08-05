


from nltk.util import ngrams
sentence = 'this is a foo bar sentences, and i want to ngramize it. way to go!'
n = 2
#split on punctuation
punctsplit = sentence.replace('.',',').split(',')


for piece in punctsplit:  
  bigrams = ngrams(piece.split(), n)
  for grams in bigrams:
    print grams


  
  
