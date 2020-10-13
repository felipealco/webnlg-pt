#!/usr/bin/python3

'''
  Calculating the Repetition Rate
  Author: Felipe Costa
  
  Originally proposed in "Cache-based Online Adaptation for Machine Translation Enhanced Computer Assisted Translation"  
'''

# database set up
import mysql.connector

mydb = mysql.connector.connect(
  host="",
  user="",
  passwd="",
  database="",
  charset='utf8'
)

mycursor = mydb.cursor()

# repetition rate function
from nltk import ngrams
from sacremoses import MosesTokenizer

def get_RR(corpus):
  mt = MosesTokenizer(lang='pt')
  
  count = {1: {}, 2: {}, 3: {}, 4:{}}

  for n in range(1, 5):
    for sentence in corpus:
      temp = ngrams(mt.tokenize(sentence[0], escape=False), n)

      for grams in temp:
        if grams not in count[n]:
          count[n][grams] = 0
        
        count[n][grams] = count[n][grams] + 1

  RR = 1

  for n in range(1, 5):
    x = len(count[n])
    for sentence in count[n]:
      if count[n][sentence] == 1:
        x -= 1
    RR *= (len(count[n]) - x)/len(count[n])
    
  return RR ** (1/4)

mycursor.execute("SELECT text FROM Lex WHERE id <= 4148;")
src = mycursor.fetchall()
print('source', get_RR(src))

mycursor.execute("SELECT text FROM Translation WHERE id <= 4148;")
mt = mycursor.fetchall()
print('machine translation', get_RR(mt))

mycursor.execute("SELECT text FROM LinearPosEditing WHERE translation_id <= 4148 and status != 'dontknow';")
pe = mycursor.fetchall()
print('post edited', get_RR(pe))
