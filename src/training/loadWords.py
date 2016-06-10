#!/usr/bin/env python

import sys
import json
import redis

# Initialize parameters
words_file = sys.argv[1]

# Initialize Redis connection
r_cli = redis.Redis()

# Read words file
src = open(words_file, 'r')
words = json.loads( src.read() )
src.close()

# Insert words to redis database
r_cli.delete('words')
for word, word_id in words.items():
  r_cli.hset('words', word, word_id)

# Ending
print 'Words import complete'
