#!/usr/bin/env python

import sys
import re
import os
import redis
import glob

import genUtils as g
import loadUtils as l

# Initialize system env
r = redis.Redis()
r.flushall()

# Get books location
books_path = glob.glob(sys.argv[1] + '/*')
r.set('file_count', len(books_path))

# Initialize tmp files
words_token_file = 'p2p-word_token.json'
idf_file = 'p2p-idf.json'
word_appr_file = 'p2p-word_appr.json'
tf_header = 'p2p-tf'
os.system('echo \'{"__total__":0}\' > ' + words_token_file)

# Gen TF
counter = 1
for book_path in books_path:
  tf_path = tf_header + str(counter)
  g.genTF(book_path, words_token_file, tf_path)
  counter += 1

# Gen IDF
g.genIDF(tf_header + '*', words_token_file, idf_file, word_appr_file)

# Load IDF
l.loadIDF(idf_file)

# Load Words
l.loadWords(words_token_file)

# Load WordAppr
l.loadWordAppr(word_appr_file)

# Delete all tmp file
os.system('rm -f p2p* *.pyc')

print "!!! Complete !!!"
