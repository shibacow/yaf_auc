#!/usr/bin/env python
# -*- coding:utf-8 -*-

from mongo_op import MongoOp

def sumofnum(mp):
    sm=sum([c['NumOfAuctions'] for c in mp.cat.find({"IsLeaf":True}) if 'NumOfAuctions' in c])
    print sm
def show_cat(mp):
    sums=0
    depth=3
    sums=sum([c['NumOfAuctions'] for c in mp.cat.find({"Depth":depth}) if 'NumOfAuctions' in c])
    print sums
    for c in mp.cat.find({"Depth":depth}):
        if 'NumOfAuctions' in c:
            nums=c['NumOfAuctions']
            if 100.0*nums/sums>0.3:
                print c['CategoryId'],c['CategoryPath'],'|',nums,'|',(1.0*nums)/sums
        else:
            pass

def main():
    mp=MongoOp('localhost')
    show_cat(mp)

if __name__=='__main__':main()
