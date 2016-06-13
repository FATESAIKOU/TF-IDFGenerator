#!/usr/bin/env python

import sys
import json
import redis

def loadIDF(idf_path):
  # Initialize parameters
  idf_file = idf_path

  # Initialize Redis connection
  r_cli = redis.Redis()

  # Read idf file
  src = open(idf_file, 'r')
  idfs = json.loads( src.read() )
  src.close()

  # Insert idfs to redis database
  r_cli.delete('idfs')
  for word_id, idf in enumerate( idfs ):
    r_cli.hset('idfs', word_id, idf)

  # Ending
  print 'Idfs import complete'


def loadWords(words_path):
  # Initialize parameters
  words_file = words_path

  # Initialize Redis connection
  r_cli = redis.Redis()

  # Read words file
  src = open(words_file, 'r')
  words = json.loads( src.read() )
  src.close()

  # Insert words to redis database
  r_cli.delete('words')
  r_cli.delete('ids')
  for word, word_id in words.items():
    r_cli.hset('words', word, word_id)
    r_cli.hset('ids', word_id, word)

  # Ending
  print 'Words & Ids import complete'


def loadWordAppr(word_appr_path):
  # Initialize parameters
  word_appr_file = word_appr_path

  # Initialize Redis connection
  r_cli = redis.Redis()

  # Read words file
  src = open(word_appr_file, 'r')
  word_apprs = json.loads( src.read() )
  src.close()

  # Insert words to redis database
  r_cli.delete('word_appr')
  for word_id, word_appr in enumerate( word_apprs ):
    r_cli.hset('word_appr', word_id, word_appr)

  # Ending
  print 'WordAppr import complete'

