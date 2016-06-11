import sys
import re
import json
import numpy
import redis
import MySQLdb

from math import log
from math import sqrt

import pycuda.autoinit
import pycuda.driver as drv

sys.path.insert(0, '/home/fatesaikou/testPY/TF-IDFGenerator/src')
from config import *

def getWords(filename):
  src = open(filename, 'r')
  words = re.sub('[^\w]', ' ', src.read()).split()
  src.close()
  return words

def genTFArray(words):
  r = redis.Redis()
  now_count = int( r.hget('words', '__total__') )
  tfs = [0] * (now_count + 1)
  appr_word_ids = []
  new_word_ids = []

  """  counting words appearence """
  for word in words:
    word_id = int(r.hget('words', word))
    if word_id is not None:
      tfs[word_id] += 1
      if tfs[word_id] == 1:
        appr_word_ids.append(word_id)
    else:
      now_count = r.hincrby('words', '__total__')
      r.hset('words', word, now_count)
      new_word_ids.append(word_id)
      tfs.append(1)

  """ update word_appr & idfs in redis """
  ''' for the words that exist in words database '''
  file_count = float(r.incr('file_count'))
  for word_id in appr_word_ids:
    appr_count = float(r.hincrby('word_appr', word_id))
    r.hset('idfs', word_id, log(file_count / (appr_count))) # ... Well, no plus one...

  ''' for the words that does NOT exist in words database '''
  for word_id in new_word_ids:
    appr_count = float(r.hset('word_appr', word_id, 1))
    r.hset('idfs', word_id, log(file_count / (appr_count)))

  return (len(words), tfs)

def genTF_IDFArray(tf, word_num):
  r = redis.Redis()
  tf_idf = [0.0] * word_num
  for word_id, count in enumerate(tf):
    tf_idf[word_id] = sqrt(float(count) / float(word_num)) * float(r.hget('idfs', word_id))

  return tf_idf

def createBookRecord(tf_idf, filename):
  db = MySQLdb.connect(mysql['host'], mysql['username'], mysql['password'], mysql['database'])
  cursor = db.cursor()

  ''' Create book record '''
  cursor.execute('INSERT INTO `books` (`path`) VALUES (\'' + db.escape_string(filename) + '\')')
  db.commit()
  book_rec = {'id': cursor.lastrowid}
  tf_list = sorted(enumerate(tf_idf), key = lambda x: x[1])

  ''' Create tf_idf record for the book '''
  query = 'INSERT INTO `tf_idfs` (`type`, `link_id`, `word_id`, `value`) VALUES '
  i = -1
  while i > -10:
    (word_id, value) = tf_list[i]
    query += '(\'book\', \'' + str(book_rec['id']) + '\', \'' + str(word_id) + '\', \'' + str(value) + '\')'
    if (i > -9): query += ','
    i -= 1
  cursor.execute(query)
  db.commit()

  book_rec['tf_idf'] = tf_idf
  return book_rec

def getSim(tf_idf, threshold):
  sim_classes = []
  sim_books = []
  return (sim_classes, sim_books)

def appendToSimClass(sim_classes, book_rec):
  return 0

def createClassRecord(sim_books, tf_idf):
  return 0

def readTF_IDF(type, id):
  if type == 'class':
    path = system_path['class_tf_idf_root'] + '/' + str(id) + '.json'
  elif type == 'book':
    path = system_path['book_tf_idf_root'] + '/' + str(id) + '.json'

  src = open(path, 'r')
  tf_idf = json.loads(src.read())
  src.close()

  return tf_idf

def saveTF_IDF(type, id, tf_idf):
  if type == 'class':
    path = system_path['class_tf_idf_root'] + '/' + str(id) + '.json'
  elif type == 'book':
    path = system_path['book_tf_idf_root'] + '/' + str(id) + '.json'

  src = open(path, 'w')
  src.write(json.dumps(tf_idf))
  src.close()

  return 0

def getDiff(a, b):
  return 0.0
