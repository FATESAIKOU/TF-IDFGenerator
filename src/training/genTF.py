#!/usr/bin/env python

import numpy
import re
import json
import sys

# Initialize program paramaters
input_file = sys.argv[1]
output_file = sys.argv[2]
word_token_file = sys.argv[3]

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
