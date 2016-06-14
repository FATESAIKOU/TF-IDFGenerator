import numpy
import sys
import pprint
import time

import utils as ut

def upload(filename, threshold):
  start = time.time()

  """ get Words from provided file """
  words = ut.getWords(filename)
  end = time.time()
  print 'Get words time:', end - start
  start = end

  """ get TF array and word number with Words"""
  (word_num, tf) = ut.genTFArray(words)
  end = time.time()
  print 'Get TF time:', end - start
  start = end

  """ get TF-IDF array with tf & word_num """
  tf_idf = ut.genTF_IDFArray(tf, word_num)
  end = time.time()
  print 'Get TF-IDF time:', end - start
  start = end

  """ create Book record at mysql database and get the record """
  book_rec = ut.createBookRecord(tf_idf, filename)
  end = time.time()
  print 'create Book time:', end - start
  start = end

  """ get all similar class & books with tf_idf & threshold """
  (sim_classes, sim_books) = ut.getSim(book_rec, tf_idf, threshold)
  end = time.time()
  print 'Get Sim time:', end - start
  start = end

  """ append to the similar class """
  ut.appendToSimClass(sim_classes, book_rec)
  end = time.time()
  print 'Append to sim class time:', end - start
  start = end

  """ if sim book_num more the one, than create a new class """
  if len(sim_books) > 1:
    ut.createClassRecord(sim_books, tf_idf)
  end = time.time()
  print 'create class time:', end - start
  start = end

  return 0
