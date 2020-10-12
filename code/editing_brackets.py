#!/usr/bin/python3

'''

  Generating Editing Bracktes from two strings on token level
  Author: Felipe Costa
  
'''

import html
import mysql.connector
import numpy as np

from sacremoses import MosesTokenizer, MosesDetokenizer

mt = MosesTokenizer(lang='pt')
md = MosesDetokenizer(lang='pt')

def LCTokenSequence(strings):
  a = strings[0]
  b = strings[1]
  
  if a == b == []:
    return ''
  
  # LCS algorithm  
  table = np.zeros(shape=(len(a) + 1, len(b) + 1), dtype=int)

  for i in range(1, len(a) + 1):
    for j in range(1, len(b) + 1):
      if a[i-1] == b[j-1]:
        table[i][j] = table[i-1][j-1] + 1
  
  i, j = np.unravel_index(table.argmax(), table.shape)
  
  x = table[i][j]
  
  # slicing LCS and leftovers
  left = [a[0:i-x], b[0:j-x]]
  common = [a[i-x:i], b[j-x:j]]
  right = [a[i:], b[j:]]
  
  if left == common: # no common substring found
    return ' [' + md.detokenize(right[0]) + '|' + md.detokenize(right[1]) + '] '
  else:
    return LCTokenSequence(left) + md.detokenize(common[0]) + LCTokenSequence(right)
  
# database connection

mydb = mysql.connector.connect(
  host="",
  user="",
  passwd="",
  database=""
)

mycursor = mydb.cursor()

mycursor.execute('  SELECT LinearPosEditing.text \
                         , Translation.text \
                    FROM LinearPosEditing \
                    INNER JOIN Translation \
                      ON LinearPosEditing.translation_id = Translation.id \
                    WHERE LinearPosEditing.translation_id <= 4148 \
                    AND LinearPosEditing.status != "dontknow";')
        
myresult = mycursor.fetchall()

for x in myresult:
  postedition, machine = x
  
  postedition = html.unescape(postedition)
  postedition = mt.tokenize(postedition, escape=False)
  
  machine = html.unescape(machine)
  machine = mt.tokenize(machine, escape=False)
  
  print(LCTokenSequence([machine, postedition]))
