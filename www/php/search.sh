#!/bin/bash

# Go to target dir
cd $1

# Execute Python file
# search.py [type] [filename / string]
$2 $3 $4

#Back to current dir
cd -
