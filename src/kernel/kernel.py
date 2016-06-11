import numpy
import sys
import pprint

import utils as ut

def upload(filename, threshold):

  """ get Words from provided file """
  words = ut.getWords(filename)

  """ get TF array and word number with Words"""
  (word_num, tf) = ut.genTFArray(words)

  """ get TF-IDF array with tf & word_num """
  tf_idf = ut.genTF_IDFArray(tf, word_num)

  """ create Book record at mysql database and get the record """
  book_rec = ut.createBookRecord(tf_idf, filename)

  """ get all similar class & books with tf_idf & threshold """
  (sim_classes, sim_books) = ut.getSim(tf_idf, threshold)

  """ append to the similar class """
  ut.appendToSimClass(sim_classes, book_rec)

  """ if sim book_num more the one, than create a new class """
  if len(sim_books) > 1:
    ut.createClassRecord(sim_books, tf_idf)

  return 0
