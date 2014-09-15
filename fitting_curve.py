#!/usr/bin/python 
# -*- coding:utf-8 -*-
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import sys
sys.path.append('./lib')
from mongo_op import MongoOp

import scipy.optimize
#from numpy import *
import numpy
import pprint
import logging
FORMAT="%(asctime)s-%(levelname)s-%(message)s"
logging.basicConfig(level=logging.INFO,format=FORMAT)
#parameter0=((1.5,1.5,1.5),
#            (0.5,0,5,0.5))
parameter0=[(a*0.1,a*0.1,a*0.1) for a in (1,2,3,5,8,13,21,34,55,89)]

def init():
    return MongoOp('localhost')

def fit_func(parameter,x,y):
    a0=parameter[0]
    a1=parameter[1]
    a2=parameter[2]
    residual=y-(a0*(x-1) - a1*((x-1)**2) + a2*((x-1)**3) + 1)
    return residual



def normalize_bidslist(bidslist):
    dk={}
    for k in ('PX','PY','APX','APY','ALLPX','ALLPY'):
        dk[k]=[]

    dkey='DateProgress'
    pkey='PriceProgress'
    for b in bidslist:
        if dkey in b and pkey in b:
            if b['IsAutomatically']=='true':
                #logging.info("true")
                dk['APX'].append(b[dkey])
                dk['APY'].append(b[pkey])
            elif b['IsAutomatically']=='false':
                #logging.info("false")
                dk['PX'].append(b[dkey])
                dk['PY'].append(b[pkey])
            dk['ALLPX'].append(b[dkey])
            dk['ALLPY'].append(b[pkey])
    for k in dk:
        dk[k]=numpy.array(dk[k])
    return dk
def verify_results(results):
    is_true=True
    for i in range(3):
        sz=[int(a[i]) for a in results]
        try:
            assert(all([sz[0]==c for c in sz])),'i={} not match {}'.format(i,sz)
        except AssertionError,err:
            is_true=False
    return is_true

def save_plt(plt,a,j): 
    aid=a['AuctionID']
    filename="graph/{}.png".format(aid)
    plt.savefig(filename)
    msg="j={} filename={}".format(j,filename)
    logging.info(msg)
def close_plt(plt):
    plt.clf()
    plt.cla()

def fit_curves(dk):
    results0=[]
    rz0=None
    results1=[]
    rz1=None
    ALLPY=dk['ALLPY']
    ALLPX=dk['ALLPX']
    PY=dk['PY']
    PX=dk['PX']
    for parameter in parameter0:
        try:
            resultA=scipy.optimize.leastsq(fit_func,parameter,args=(ALLPX,ALLPY),full_output=False)
            results0.append(resultA[0])
            rz0=resultA
            resultB=scipy.optimize.leastsq(fit_func,parameter,args=(PX,PY),full_output=False)
            results1.append(resultB[0])
            rz1=resultB
        except TypeError,err:
            print err
            return None,[],None,[]
    results0=numpy.array(results0)
    results1=numpy.array(results1)
    return rz0,results0,rz1,results1

def draw_curve(plt,rz,color):
    xlist=numpy.linspace(0,1,100)
    #residual=y-(a0*(x-1) - a1*((x-1)**2) + a2*((x-1)**3) + 1)
    ylist=[]
    a0=rz[0][0]
    a1=rz[0][1]
    a2=rz[0][2]
    for x in xlist:
        y=a0*(x-1) - a1*((x-1)**2) + a2*((x-1)**3) + 1
        ylist.append(y)
    ylist=numpy.array(ylist)
    plt.plot(xlist,ylist,color=color)

def gen_differentiate(plt,rz,color):
    xlist=[0.2,0.4,0.6,0.8,0.9]
    a0=rz[0][0]
    a1=rz[0][1]
    a2=rz[0][2]
    for x in xlist:
        slope=3*a2*(x**2)- 2*x*(3*a2-a1) + 2*a1 + a0 + 3* a2
        y=a0*(x-1) - a1*((x-1)**2) + a2*((x-1)**3) + 1
        b=y-(slope*x)
        #print "x={} y={} slope={}".format(x,y,slope)
        x0=[x,x+0.1]
        fx=lambda aa:slope*aa + b
        y0=[fx(xa) for xa in x0]
        #print "x0={} y0={}".format(x0,y0)
        plt.plot(x0,y0,color=color)
def main():
    mp=init()
    matchcnt=[0,0]
    for j,a in enumerate(mp.enditem.find().limit(10)):
        assert(a['bidslist'])
        dk=normalize_bidslist(a['bidslist'])
        rz0,results0,rz1,results1=fit_curves(dk)
        if rz0 and rz1 and verify_results(results0) and verify_results(results1):
            plt.scatter(dk['APX'],dk['APY'],color='green')
            plt.scatter(dk['PX'],dk['PY'],color='red')
            draw_curve(plt,rz0,'blue')
            draw_curve(plt,rz1,'pink')
            gen_differentiate(plt,rz0,color='green')
            gen_differentiate(plt,rz1,color='yellow')
            save_plt(plt,a,j)
            close_plt(plt)
if __name__=='__main__':main()
