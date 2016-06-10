#!/usr/bin/env python

import sys
import json
import redis

# Initialize parameters
idf_file = sys.argv[1]

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
print 'complete'
