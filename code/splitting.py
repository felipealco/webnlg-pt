#!/usr/bin/python3
'''
  Splitting data for model
  Author: Felipe Costa
  
  Splitted on 6:2:2, training, test, and development 
  
  Steps:
  1 - save good sentences (score > 2) to good set
  2 - save bad sentences (score <= 2) to all file
  3 - split good set into test and temp sets
  4 - save test set in test file
  5 - split temp set into train and dev sets
  6 - save train set to train file, save dev set to dev file, and append train set to all file
  
  |------------------------------------------------------------------------------------------|
  |                                      all sentences                                       |
  |------------------------------------------------------------------------------------------|
  |      bad sentences      |                 good sentences                                 |
  |------------------------------------------------------------------------------------------|
  |      bad sentences      |           temp set                          |     test set     | 
  |------------------------------------------------------------------------------------------|
  |      bad sentences      |           train set       |     dev set     |     test set     | 
  |------------------------------------------------------------------------------------------|
  |                      train set                      |     dev set     |     test set     |     <- ALL model
  |------------------------------------------------------------------------------------------|
                            |           train set       |     dev set     |     test set     |     <- GOOD model
                            |----------------------------------------------------------------|
                                    
  dev and test set are shared by both models, and GOOD's train set is a subset of ALL's train set

'''

import html

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


# tokenizer set up
from sacremoses import MosesTokenizer

mt = MosesTokenizer(lang='pt')


# getting translations
mycursor.execute("SELECT Translation.id \
                       , Entry.category_id \
                       , Entry.size \
                       , Translation.text \
                       , Lex.text \
                       , Evaluation.score \
                  FROM Translation \
                  INNER JOIN Evaluation \
                    ON Translation.id = Evaluation.table_id \
                  INNER JOIN Lex \
                    ON Translation.lex_id = Lex.id \
                  INNER JOIN Entry \
                    ON Lex.entry_id = Entry.id \
                  WHERE Translation.id <= 4148 \
                  AND Evaluation.source_table = 'Translation';")

myresult = mycursor.fetchall()

sentences = {}

for i in myresult:
  translation_id, cat, size, machine, original, score = i
  
  machine = html.unescape(machine)
  machine = mt.tokenize(machine, return_str=True, escape=False)

  original = html.unescape(original)
  original = mt.tokenize(original, return_str=True, escape=False)
  
  if translation_id not in sentences:
    sentences[translation_id] = {
      'category': str(cat),
      'size': str(size),
      'original': original,
      'translation': machine, 
      'posteditions': list(),
      'translation_score': int(score),
      'postediting_score': list()
      }


# getting posteditions

mycursor.execute("SELECT LinearPosEditing.translation_id \
                       , LinearPosEditing.text \
                       , Evaluation.score \
                  FROM LinearPosEditing \
                  INNER JOIN Evaluation \
                    ON LinearPosEditing.id = Evaluation.table_id \
                  WHERE LinearPosEditing.translation_id <= 4148 \
                  AND LinearPosEditing.status != 'dontknow' \
                  AND Evaluation.source_table = 'LinearPosEditing';")

myresult = mycursor.fetchall()

for i in myresult:
  translation_id, text, score = i
  
  text = html.unescape(text)
  text = mt.tokenize(text, return_str=True, escape=False)

  if text not in sentences[translation_id]['posteditions']:
    sentences[translation_id]['posteditions'].append(text)
    sentences[translation_id]['postediting_score'].append(score)

good = {
  'source': list(),
  'target': list(),
  'original': list(),
  'size': list()
  }
  
temp = {
  'source': list(),
  'target': list(),
  'original': list(),
  'size': list()
  }

allSrc = open('all.train.src', 'w')
allTrg = open('all.train.trg', 'w')
allOrg = open('all.train.org', 'w')

trainSrc = open('good.train.src', 'w')
trainTrg = open('good.train.trg', 'w')
trainOrg = open('good.train.org', 'w')

testSrc = open('test.src', 'w')
testTrg = open('test.trg', 'w')
testOrg = open('test.org', 'w')

devSrc = open('dev.src', 'w')
devTrg = open('dev.trg', 'w')
devOrg = open('dev.org', 'w')

for i in sentences:
  item = sentences[i]
  
  for j in range(len(item['posteditions'])):
    if item['postediting_score'][j] > 2:
      good['source'].append([item['translation']])
      good['target'].append([item['posteditions'][j]])
      good['original'].append([item['original']])
      good['size'].append(item['size'])
    else:
      allSrc.write(item['translation'] + '\n')
      allTrg.write(item['posteditions'][j] + '\n')
      allOrg.write(item['original'] + '\n')

from sklearn.model_selection import StratifiedShuffleSplit

sss = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=42)

for train_index, test_index in sss.split(good['source'], good['size']):

  for i in train_index:
    temp['source'].append(good['source'][i])
    temp['target'].append(good['target'][i])
    temp['original'].append(good['original'][i])
    temp['size'].append(good['size'][i])
  
  for i in test_index:
    testSrc.write(good['source'][i][0] + '\n')
    testTrg.write(good['target'][i][0] + '\n')
    testOrg.write(good['original'][i][0] + '\n')

sss = StratifiedShuffleSplit(n_splits=1, test_size=0.25, random_state=42)
      
for train_index, dev_index in sss.split(temp['source'], temp['size']):
  for i in train_index:
    trainSrc.write(temp['source'][i][0] + '\n')
    trainTrg.write(temp['target'][i][0] + '\n')
    trainOrg.write(temp['original'][i][0] + '\n')
    
    allSrc.write(temp['source'][i][0] + '\n')
    allTrg.write(temp['target'][i][0] + '\n')
    allOrg.write(temp['original'][i][0] + '\n')
  
  for i in dev_index:
    devSrc.write(temp['source'][i][0] + '\n')
    devTrg.write(temp['target'][i][0] + '\n')
    devOrg.write(temp['original'][i][0] + '\n')      
