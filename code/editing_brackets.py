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
   
  table = np.zeros(shape=(len(a) + 1, len(b) + 1), dtype=int)

  for i in range(1, len(a) + 1):
    for j in range(1, len(b) + 1):
      if a[i-1] == b[j-1]:
        table[i][j] = table[i-1][j-1] + 1
  
  i, j = np.unravel_index(table.argmax(), table.shape)
  
  x = table[i][j]
  
  left = [a[0:i-x], b[0:j-x]]
  common = [a[i-x:i], b[j-x:j]]
  right = [a[i:], b[j:]]
  
  if left == common:
    temp = '[' + ''.join(right[0]) + '|' + ''.join(right[1]) + ']'
    
    # removing spaces from begining and end of editions
    if len(right[0]) > 1 and right[0][0] == ' ':
      temp = ' [' + ''.join(right[0][1:]) + '|' + ''.join(right[1]) + ']'

    if len(right[1]) > 1 and right[1][0] == ' ':
      temp = ' [' + ''.join(right[0]) + '|' + ''.join(right[1][1:]) + ']'
    
    if len(right[0]) > 1 and right[0][-1] == ' ':
      temp = '[' + ''.join(right[0][:-1]) + '|' + ''.join(right[1]) + '] '
    
    if len(right[1]) > 1 and right[1][-1] == ' ':
      temp = '[' + ''.join(right[0]) + '|' + ''.join(right[1][:-1]) + '] '
    
    return temp
  else:
    return LCTokenSequence(left) + ''.join(common[0]) + LCTokenSequence(right)
  

mydb = mysql.connector.connect(
  host="",
  user="",
  passwd="",
  database="",
  charset='utf8'
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
  postedition = md.detokenize(postedition.split(' '))
  postedition = mt.tokenize(postedition, escape=False, return_str=True)
  postedition = list(postedition)
  
  machine = html.unescape(machine)
  machine = mt.tokenize(machine, escape=False, return_str=True)
  machine = list(machine)
  
  print(LCTokenSequence([machine, postedition]))
