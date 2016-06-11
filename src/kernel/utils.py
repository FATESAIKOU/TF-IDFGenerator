import sys
import re
import json
import numpy
import redis
import MySQLdb
from math import log

import pycuda.autoinit
import pycuda.driver as drv

sys.path.insert(0, '/home/fatesaikou/testPY/TF-IDFGenerator/src')
import config

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
    r.hset('idfs', word_id, log(file_count / (appr_count + 1)))

  ''' for the words that does NOT exist in words database '''
  for word_id in new_word_ids:
    appr_count = float(r.hset('word_appr', word_id, 1))
    r.hset('idfs', word_id, log(file_count / (appr_count + 1)))

  return (len(words), tfs)

def genTF_IDFArray(tf, word_num):
  tf_idf = []
  return tf_idf

def createBookRecord(tf_idf, filename):
  book_rec = {}
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
  tf_idf = []
  return tf_idf

def saveTF_IDF(type, id):
    return 0

def getDiff(a, b):
  return 0.0
