#!/usr/bin/env python

import numpy
import json
import glob
import sys

from math import log

# Initialize program paramaters
input_files = glob.glob(sys.argv[1] + '*.json')
word_token_file = sys.argv[2]
output_file = sys.argv[3]

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
  idf[word_id] = log( file_num / ( count ) )

# Output IDF
output = open(output_file, 'w')
output.write( json.dumps( idf ) )
output.close()

print "IDF len", len(idf)
