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

if(type == 'string'):
  " File => [Request String] "
  src = open('/tmp/phpTemp', 'w')
  src.write(file)
  src.close()

  file = '/tmp/phpTemp'

" Upload File By Kernel "
(sim_classes, sim_books) = kernel.upload(file, 0.1)

result = {}
result['books'] = {}
result['books_keyword'] = {}
result['classes_books_num'] = {}
result['classes_keyword'] = {}

" Get Books "
" book[0] => book_id "
" book[1] => book_path "
cursor.execute('SELECT * FROM books')
for book in cursor.fetchall():
  book_id = str(book[0])
  result['books'][book_id] = book[1]

" Get Classes Books Number "
for e in enumerate(sim_classes):
  " get books_num "
  " e[1][0] => class_id "
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

" Get Keyword By Books"
for e in enumerate(sim_books):
  book_id = str(e[1][0])
  cursor.execute('SELECT * FROM tf_idfs WHERE type="book" AND link_id=' + book_id)

  item = {}
  for word_item in cursor.fetchall():
    word_id = word_item[2]
    item['word'] = r.hget('ids', word_id)
    item['value'] = word_item[3]
    item['book_id'] = book_id
    result['books_keyword'][word_id] = item


src = open('answer_demonic.json', 'w')
src.write(json.dumps(result))
src.close()
