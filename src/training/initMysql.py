#!/usr/bin/env python

import sys
import MySQLdb

sys.path.insert(0, '/home/fatesaikou/testPY/TF-IDFGenerator/src')
from config import mysql

db = MySQLdb.connect(mysql['host'], mysql['username'], mysql['password'], mysql['database'])
cursor = db.cursor()
cursor.execute('DROP DATABASE mylib;')
cursor.execute('CREATE DATABASE mylib;')

db = MySQLdb.connect(mysql['host'], mysql['username'], mysql['password'], mysql['database'])
cursor = db.cursor()
cursor.execute('CREATE TABLE books (id INT(11) auto_increment primary key, path TEXT(512) NOT NULL);')
cursor.execute('CREATE TABLE classes (id INT(11) auto_increment primary key, book_num INT(11) default 0);')
cursor.execute('CREATE TABLE tf_idfs (type ENUM(\'class\', \'book\'), link_id INT(11) NOT NULL, word_id INT(11) NOT NULL,  value DOUBLE);')
cursor.execute('CREATE TABLE book_class (b_id INT(11), c_id INT(11), cos_diff DOUBLE);')

print 'DB migration complete!!'
