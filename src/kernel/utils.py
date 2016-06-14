import sys
import re
import json
import redis
import pprint
import MySQLdb

from math import log
from math import sqrt

import numpy as np
import pycuda.autoinit
import pycuda.driver as cuda
from pycuda.compiler import SourceModule

sys.path.insert(0, '/home/fatesaikou/testPY/TF-IDFGenerator/src')
from config import *

def getWords(filename):
  src = open(filename, 'r')
  words = re.sub('[^\w]', ' ', src.read()).split()
  src.close()
  return words

def genTFArray(words):
  r = redis.Redis()
  now_count = int( r.hget('words', '__total__') )
  tfs = [0] * (now_count + 1)
  appr_word_ids = []
  new_word_ids = []

  """  counting words appearence """
  for word in words:
    word_id = r.hget('words', word)
    if word_id is not None:
      word_id = int(word_id)
      tfs[word_id] += 1
      if tfs[word_id] == 1:
        appr_word_ids.append(word_id)
    else:
      now_count = r.hincrby('words', '__total__')
      r.hset('words', word, now_count)
      r.hset('ids', now_count, word)
      new_word_ids.append(now_count)
      tfs.append(1)

  """ update word_appr & idfs in redis """
  ''' for the words that exist in words database '''
  file_count = float(r.incr('file_count'))
  for word_id in appr_word_ids:
    appr_count = float(r.hincrby('word_appr', word_id))
    r.hset('idfs', word_id, log(file_count / (appr_count))) # ... Well, no plus one...

  ''' for the words that does NOT exist in words database '''
  for word_id in new_word_ids:
    appr_count = float(r.hset('word_appr', word_id, 1))
    r.hset('idfs', word_id, log(file_count / (appr_count)))

  return (int(r.hget('words', '__total__')), tfs)

def genTF_IDFArray(tf, word_num):
  r = redis.Redis()
  tf_idf = [0.0] * (word_num + 1)
  for word_id, count in enumerate(tf):
    if count > 0:
      tf_idf[word_id] = sqrt(float(count) / float(word_num)) * float(r.hget('idfs', word_id))
    else:
      tf_idf[word_id] = 0

  return tf_idf

def createBookRecord(tf_idf, filename):
  db = MySQLdb.connect(mysql['host'], mysql['username'], mysql['password'], mysql['database'])
  cursor = db.cursor()

  ''' Create book record '''
  cursor.execute('INSERT INTO `books` (`path`) VALUES (\'' + db.escape_string(filename) + '\')')
  db.commit()
  book_rec = {'id': cursor.lastrowid}
  tf_list = sorted(enumerate(tf_idf), key = lambda x: x[1])

  ''' Create tf_idf record for the book '''
  query = 'INSERT INTO `tf_idfs` (`type`, `link_id`, `word_id`, `value`) VALUES '
  i = -1
  while i > -10:
    (word_id, value) = tf_list[i]
    query += '(\'book\', \'' + str(book_rec['id']) + '\', \'' + str(word_id) + '\', \'' + str(value) + '\')'
    if (i > -9): query += ','
    i -= 1
  cursor.execute(query)
  db.commit()
  db.close()

  ''' Saving tf-idf record to system '''
  saveTF_IDF('book', book_rec['id'], tf_idf)

  book_rec['tf_idf'] = tf_idf
  return book_rec

def createClassRecord(sim_books, tf_idf):
  db = MySQLdb.connect(mysql['host'], mysql['username'], mysql['password'], mysql['database'])
  cursor = db.cursor()

  ''' Create class record '''
  cursor.execute('INSERT INTO `classes` (`book_num`) VALUES (\'' + str(len(sim_books)) + '\')')
  db.commit()
  class_rec = {'id': cursor.lastrowid}
  tf_list = sorted(enumerate(tf_idf), key = lambda x: x[1])

  ''' Create tf_idf record for the class '''
  query = 'INSERT INTO `tf_idfs` (`type`, `link_id`, `word_id`, `value`) VALUES '
  i = -1
  while i > -10:
    (word_id, value) = tf_list[i]
    query += '(\'class\', \'' + str(class_rec['id']) + '\', \'' + str(word_id) + '\', \'' + str(value) + '\'),'
    i -= 1
  cursor.execute(query[:-1])
  db.commit()

  ''' Create Book to Class record '''
  query = 'INSERT INTO `book_class` (`b_id`, `c_id`, `cos_diff`) VALUES '
  for book_id, cos_diff in sim_books:
    query += '(\'' + str(book_id) + '\', \'' + str(class_rec['id']) + '\', \'' + str(cos_diff) + '\'),'
    ''' This may exceed mysql's limit of query string length !! '''

  cursor.execute(query[:-1])
  db.commit()

  ''' Saving tf-idf record to system '''
  saveTF_IDF('class', class_rec['id'], tf_idf)

  return 0

def appendToSimClass(sim_classes, book_rec):
  db = MySQLdb.connect(mysql['host'], mysql['username'], mysql['password'], mysql['database'])
  cursor = db.cursor()

  for class_id, new_tf_idf, cos_diff in sim_classes:
    cursor.execute('INSERT INTO `book_class` (`b_id`, `c_id`, `cos_diff`) VALUES (\'' + str(book_rec['id']) + '\', \'' + str(class_id) + '\', \'' + str(cos_diff) + '\')')
    saveTF_IDF('class', class_id, new_tf_idf)
    cursor.execute('UPDATE `classes` SET `book_num` = `book_num` + 1 WHERE `id` = ' + str(class_id))

  db.commit()

  return 0

def readTF_IDF(type, id):
  if type == 'class':
    path = system_path['class_tf_idf_root'] + '/' + str(id) + '.json'
  elif type == 'book':
    path = system_path['book_tf_idf_root'] + '/' + str(id) + '.json'

  src = open(path, 'r')
  tf_idf = json.loads(src.read())
  src.close()

  return tf_idf

def saveTF_IDF(type, id, tf_idf):
  if type == 'class':
    path = system_path['class_tf_idf_root'] + '/' + str(id) + '.json'
  elif type == 'book':
    path = system_path['book_tf_idf_root'] + '/' + str(id) + '.json'

  src = open(path, 'w')
  src.write(json.dumps(tf_idf))
  src.close()

  return 0

def getSim(book_rec, tf_idf, threshold):
  db = MySQLdb.connect(mysql['host'], mysql['username'], mysql['password'], mysql['database'])
  cursor = db.cursor()
  r = redis.Redis()

  size = int(r.hget('words', '__total__')) + 1
  np_tf_idf = np.array(tf_idf)
  sim_classes = []
  sim_books = []

  class_id_str = '0'
  cursor.execute('SELECT * FROM `classes`')
  for class_item in cursor.fetchall():
    class_id = class_item[0]
    c_tf_idf = readTF_IDF('class', class_id)

    np_c_tf_idf = np.array(c_tf_idf).astype(np.float32)
    np_c_tf_idf.resize(size)
    cos_diff = getDiff(np_tf_idf, np_c_tf_idf)

    if cos_diff < threshold:
      c_tf_idf = ( (np_c_tf_idf * class_item[1] + np_tf_idf) / float(class_item[1] + 1) ).tolist()
      sim_classes.append( (class_id, c_tf_idf, cos_diff) )
      class_id_str += ',' + str(class_id)

  cursor.execute('SELECT distinct(`books`.`id`) FROM `books` LEFT JOIN `book_class` on `book_class`.`b_id` = `books`.`id` and `book_class`.`c_id` NOT IN (' + class_id_str + ')')
  for book_item in cursor.fetchall():
    if book_item[0] == book_rec['id']:
      continue

    book_id = book_item[0]
    b_tf_idf = readTF_IDF('book', book_id)

    np_b_tf_idf = np.array(b_tf_idf)
    np_b_tf_idf.resize(size)
    cos_diff = getDiff(np_tf_idf, np_b_tf_idf)

    if cos_diff < threshold:
      sim_books.append((book_id, cos_diff))

  sim_books.append((book_rec['id'], 0.0))

  return (sim_classes, sim_books)

def getDiff(np_a, np_b):
  return sum(np_a * np_b) / float(sqrt(sum(np_a**2)) + sqrt(sum(np_b**2)))

def getDiffGpu(np_a, np_b):
  mod = SourceModule("""
    __global__ void mult(float *dest, float *a, float *b, int limit)
    {
      int jump_size = blockDim.x * gridDim.x;
      int offset = threadIdx.x + blockDim.x * blockIdx.x;

      int index;
      for (index = offset; index < limit; index += jump_size) {
        dest[index] = a[index] * b[index];
      }
    }

    __global__ void power2(float *dest, float *a, int limit)
    {
      int jump_size = blockDim.x * gridDim.x;
      int offset = threadIdx.x + blockDim.x * blockIdx.x;

      int index = offset;
      //for (index = offset; index < limit; index += jump_size) {
      if (index < 0) {
        dest[index] = a[index] * a[index];
      }
    }
  """)

  mult = mod.get_function("mult")
  power = mod.get_function("power2")

  a_gpu = cuda.mem_alloc(np_a.nbytes)
  b_gpu = cuda.mem_alloc(np_b.nbytes)
  mult_res_gpu = cuda.mem_alloc(np_a.nbytes)

  cuda.memcpy_htod(a_gpu, np_a)
  cuda.memcpy_htod(b_gpu, np_b)
  mult(mult_res_gpu, a_gpu, b_gpu, np.int32(np_a.size), block = (1024, 1, 1), grid = (1, 1, 1))
  #power(a_gpu, a_gpu, np.int32(np_a.size), block = (256, 1, 1), grid = (128, 1, 1))
  #power(b_gpu, b_gpu, np.int32(np_b.size), block = (256, 1, 1), grid = (128, 1, 1))

  #pow_a = np.zeros_like(np_a)
  #pow_b = np.zeros_like(np_b)
  mult_res = np.zeros_like(np_a)

  #cuda.memcpy_dtoh(pow_a, a_gpu)
  #cuda.memcpy_dtoh(pow_b, b_gpu)
  cuda.memcpy_dtoh(mult_res, mult_res_gpu)
  pprint.pprint(mult_res)

  #return mult_res.sum() / float( sqrt(pow_a.sum()) + sqrt(pow_b.sum()) )






