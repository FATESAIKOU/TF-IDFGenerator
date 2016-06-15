import numpy
import sys
import pprint
import time

import utils as ut

def upload(filename, threshold, show_times = []):
  start = time.time()

  """ get Words from provided file """
  words = ut.getWords(filename)
  end = time.time()
  if ('get_words' in show_times) or ('*' in show_times):
    print 'Get words time:\t\t', end - start
  start = end

  """ get TF array and word number with Words"""
  (word_num, tf) = ut.genTFArray(words)
  end = time.time()
  if ('get_tf' in show_times) or ('*' in show_times):
    print 'Get TF time:\t\t', end - start
  start = end

  """ get TF-IDF array with tf & word_num """
  tf_idf = ut.genTF_IDFArray(tf, word_num)
  end = time.time()
  if ('get_tf_idf' in show_times) or ('*' in show_times):
    print 'Get TF-IDF time:\t', end - start
  start = end

  """ create Book record at mysql database and get the record """
  book_rec = ut.createBookRecord(tf_idf, filename)
  end = time.time()
  if ('create_book_rec' in show_times) or ('*' in show_times):
    print 'create Book time:\t', end - start
  start = end

  """ get all similar class & books with tf_idf & threshold """
  (sim_classes, sim_books) = ut.getSim(book_rec, tf_idf, threshold)
  end = time.time()
  if ('get_sim' in show_times) or ('*' in show_times):
    print 'Get Sim time:\t\t', end - start
  start = end

  """ append to the similar class """
  ut.appendToSimClass(sim_classes, book_rec)
  end = time.time()
  if ('append_class' in show_times) or ('*' in show_times):
    print 'Append sim class time:\t', end - start
  start = end

  """ if sim book_num more the one, than create a new class """
  if len(sim_books) > 1:
    ut.createClassRecord(sim_books, tf_idf)
  end = time.time()
  if ('create_class' in show_times) or ('*' in show_times):
    print 'create class time:\t', end - start
  start = end

  return 0
