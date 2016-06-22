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

result = {}
result['books'] = {}

" prepare books data "
" Get Books "
" book[0] => book_id "
" book[1] => book_path "
cursor.execute('SELECT * FROM books')
for book in cursor.fetchall():
  book_id = str(book[0])
  result['books'][book_id] = book[1]


if(type == 'string'):
  word_id = r.hget('words', file)

  if(word_id == None):
    result['status'] = 'fail'

    " Write Result to file "
    src = open('answer_demonic.json', 'w')
    src.write(json.dumps(result))
    src.close()

    sys.exit(0)

  result['status'] = 'success'
  cursor.execute('SELECT * FROM tf_idfs WHERE type="book" AND word_id=' + word_id)

  result['tf_idf'] = {}
  for tf_idf in cursor.fetchall():
    book_id = str(tf_idf[1])
    word_id = str(tf_idf[2])

    item = {};
    item['book_name'] = result['books'][book_id]
    item['book_id'] = book_id
    item['word_name'] = r.hget('ids', word_id)
    item['word_id'] = word_id
    item['value'] = tf_idf[3]

    result['tf_idf'][book_id] = item
elif(type == 'file'):
  " Upload File By Kernel "
  (sim_classes, sim_books) = kernel.upload(file, 0.8)

  result['books_keyword'] = {}
  result['classes_books_num'] = {}
  result['classes_keyword'] = {}

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
    cursor.execute('SELECT * FROM tf_idfs WHERE type="class" AND link_id=' + class_id)
    for word_item in cursor.fetchall():
      word_id = word_item[2]

      " new Object "
      item = {}
      item['word'] = r.hget('ids', word_id)
      item['value'] = word_item[3]
      item['class_id'] = class_id
      result['classes_keyword'][word_id] = item

  " Get Keyword By Books"
  for e in enumerate(sim_books):
    book_id = str(e[1][0])
    cursor.execute('SELECT * FROM tf_idfs WHERE type="book" AND link_id=' + book_id)

    for word_item in cursor.fetchall():
      word_id = word_item[2]

      " new Object "
      item = {}
      item['word'] = r.hget('ids', word_id)
      item['value'] = word_item[3]
      item['book_id'] = book_id
      result['books_keyword'][word_id] = item


" Write Result to file "
src = open('answer_demonic.json', 'w')
src.write(json.dumps(result))
src.close()

