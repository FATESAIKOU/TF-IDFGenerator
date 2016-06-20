#!/usr/bin/env python

import sys
import json
import redis
import MySQLdb
import pprint

sys.path.insert(0, '../kernel')
import kernel
from config import *

" init mysql "
db = MySQLdb.connect(mysql['host'], mysql['username'], mysql['password'], mysql['database'])
cursor = db.cursor()

" init redis "
r = redis.Redis()

" get Attribute "
type = sys.argv[1]
file = sys.argv[2]

if(type == 'file'):
  " upload file "
  (sim_classes, sim_books) = kernel.upload(file, 0.1)

  result = {}
  result['sim_books'] = []
  for e in enumerate(sim_books):
    result['sim_books'].append(e[1])

  " Get Classes Books Number "
  result['classes_books_num'] = {}
  result['classes_keyword'] = {}
  for e in enumerate(sim_classes):
    " get books_num "
    " e[1][0] => class_id "
    print e[1][0]
    class_id = str(e[1][0])
    cursor.execute('SELECT * FROM classes WHERE id=' + class_id)
    for class_item in cursor.fetchall():
      result['classes_books_num'][class_item[0]] = class_item[1]

    " get keyword from class "
    " word_item "
    " 0 type"
    " 1 link_id"
    " 2 word_id"
    " 3 value"
    item = {}
    cursor.execute('SELECT * FROM tf_idfs WHERE type="class" AND link_id=' + class_id)
    for word_item in cursor.fetchall():
      word_id = word_item[2]
      item['word'] = r.hget('ids', word_id)
      item['value'] = word_item[3]
      item['class_id'] = class_id
      result['classes_keyword'][word_id] = item

  src = open('answer_demonic.json', 'w')
  src.write(json.dumps(result))
  src.close()

elif(type == 'string'):
  print 'Hello'

