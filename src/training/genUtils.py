#!/usr/bin/env python

import numpy
import re
import json
import glob
import sys

from math import log
from math import sqrt

def genTF(file_path, words_token_path, tf_path):
  # Initialize program paramaters
  input_file = file_path
  output_file = tf_path
  word_token_file = words_token_path

  # Read file content
  src = open(input_file, 'r')
  content = src.read()
  src.close()

  src_token = open(word_token_file, 'r')
  word_ids = json.loads( src_token.read() )
  src_token.close()

  # Get words
  words = re.sub('[^\w]', ' ', content).split();

  # Counting
  now_max = word_ids['__total__']
  tf_array = [0] * (now_max + 1)

  tf_array[0] = len(words)
  for word in words:
    if word_ids.has_key(word):
      tf_array[ word_ids[word] ] += 1
    else:
      word_ids['__total__'] += 1
      word_ids[word] = word_ids['__total__']
      tf_array.append(1)

  # Output
  output = open(output_file, 'w')
  output.write( json.dumps( tf_array ) )
  output.close()

  output_token = open(word_token_file, 'w')
  output_token.write( json.dumps( word_ids ) )
  output_token.close()


def genIDF(tfs_pattern, words_token_path, idf_path, word_appr_path):
  # Initialize program paramaters
  input_files = glob.glob(tfs_pattern)
  word_token_file = words_token_path
  output_file = idf_path
  output_word_appr_file = word_appr_path

  # Read words
  src_token = open(word_token_file, 'r')
  words = json.loads( src_token.read() )
  src_token.close()

  # Read TF list
  dir_count = [0] * (words['__total__'] + 1)
  for file_name in input_files:
    src = open(file_name)

    book_tfs = json.loads( src.read() )
    for word_id, count in enumerate( book_tfs ):
      dir_count[word_id] += 1

    src.close()

  # Gen IDF
  idf = [0] * (words['__total__'] + 1)
  file_num = float( len( input_files ) )
  for word_id, count in enumerate( dir_count ):
    idf[word_id] = log( file_num / ( count + 1.0 ) )

  # Output IDF
  output = open(output_file, 'w')
  output.write( json.dumps( idf ) )
  output.close()

  output_word_appr = open(output_word_appr_file, 'w')
  output_word_appr.write( json.dumps( dir_count ) )
  output_word_appr.close()

  print "IDF len", len(idf)
