#!/usr/bin/env python

"cuda library"
import pycuda.autoinit
import pycuda.driver as cuda
from pycuda.compiler import SourceModule

"math library"
import numpy as np
from math import sqrt

"normal library"
import json
import sys
import os

def genSVD():
  dir = '../../jsons/tf_idf/book/'
  list = os.listdir(dir)

  origin = []

  for idx, e in enumerate(list):
    src = open(dir+e, 'r')
    tf_idf = json.loads( src.read() )
    src.close()

    origin.append(tf_idf)

  origin = np.transpose(origin)

  (T, sigma, D) = np.linalg.svd(origin, False)

  return (T, sigma, D)

def main():
  mod = SourceModule("""
    __global__ void diff(double *dest, double *a, double *b, int limit)
    {
      int jump_size = blockDim.x * gridDim.x;
      int offset = threadIdx.x + blockDim.x * blockIdx.x;

      int index;
      for (index = offset; index < limit; index += jump_size) {
        dest[index] = a[index] - b[index];
      }
    }

    __global__ void power2(double *dest, double *a, int limit)
    {
      int jump_size = blockDim.x * gridDim.x;
      int offset = threadIdx.x + blockDim.x * blockIdx.x;

      int index = offset;
      for (index = offset; index < limit; index += jump_size) {
        dest[index] = a[index] * a[index];
      }
    }
  """)
  diff = mod.get_function('diff')
  pow2 = mod.get_function('power2')

  "SVD"
  (T, sigma, D) = genSVD()

  "normalize"
  D = np.absolute(D)
  row_sums = D.sum(axis=1, keepdims=True)
  D = D / row_sums
  D = np.nan_to_num(D)

  answer = {}
  for i, e1 in enumerate(D):
    answer[i] = []
    for j, e2 in enumerate(D):
      R = genDistanceGPU(e1, e2, diff, pow2)
      answer[i].append(R)

  return D, row_sums, answer

def genDistanceGPU(np_a, np_b, diff, power):
  "init variable"
  "device"
  a_gpu = cuda.mem_alloc(np_a.nbytes)
  b_gpu = cuda.mem_alloc(np_b.nbytes)
  diff_res_gpu = cuda.mem_alloc(np_a.nbytes)
  "host"
  diff_res = np.zeros_like(np_a)

  "copy to device"
  cuda.memcpy_htod(a_gpu, np_a)
  cuda.memcpy_htod(b_gpu, np_b)

  "execute cuda"
  "diff"
  diff(diff_res_gpu, a_gpu, b_gpu, np.int32(np_a.size), block = (1024, 1, 1), grid = (128, 1, 1))

  "pow2"
  power(diff_res_gpu, diff_res_gpu, np.int32(np_a.size), block = (1024, 1, 1), grid = (128, 1, 1))

  "callback"
  cuda.memcpy_dtoh(diff_res, diff_res_gpu)

  return sqrt(diff_res.sum())

