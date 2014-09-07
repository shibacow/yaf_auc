#!/usr/bin/python
# -*- coding:utf-8 -*-
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
#import pylab.plot as plt
x = [1,2,3,4,5,6]
y = [2,5,4,6,8,7]
plt.plot(x,y)

filename = "output2.png"
plt.savefig(filename)
