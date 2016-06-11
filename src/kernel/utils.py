import sys
import re
import json
import numpy
import redis
import MySQLdb

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
  tf = []
  return (len(words), tf)

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
