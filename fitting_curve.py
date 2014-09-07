#!/usr/bin/python 
# -*- coding:utf-8 -*-

import scipy.optimize
#from numpy import *
import numpy
import pprint

#データ組を作っておく
Px=[-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]
Py=[24.1, 15.0, 7.9, 3.1, -0.1, -1.2, 0.05, 3.01, 8.1, 15.2, 23.98]

#データリストを配列(array)型に変換する
Px=numpy.array(Px)
Py=numpy.array(Py)

#初期値を入力する
parameter0=[0.9,-0.5]
parameter0=[0.5,0.5]


def fit_func(parameter,x,y):
    a=parameter[0]
    b=parameter[1]
    residual=y-(a*x*x+b)
    return residual

result=scipy.optimize.leastsq(fit_func,parameter0,args=(Px,Py))

print result[0]
print 'a=', result[0][0]
print 'b=', result[0][1]
pprint.pprint(result)

