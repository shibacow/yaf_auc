#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
sys.path.append('lib')
from mongo_op import MongoOp
from datetime import datetime,timedelta
import pprint
import logging
FORMAT="%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO,format=FORMAT)


from common import time_profile

def init():
    return MongoOp('localhost')

def parse(l):
    AuctionID,endtime,bids=l.split(',')
    bids=int(bids)
    endtime=datetime.strptime(endtime,'%Y-%m-%d %H:%M:%S')
    return dict(AuctionID=AuctionID,EndTime=endtime,Bids=bids)
def save(mp,d):
    key='enditemseed'
    if not mp.has_enditem(key,d['AuctionID']):
        mp.enditem_save(key,d)
def main():
    mp=init()
    for i,l in enumerate(open('end_list.txt').readlines()):
        l=l.strip()
        d=parse(l)
        save(mp,d)
        if i%1000==0:
            print i,d
            #pprint.pprint(d)
if __name__=='__main__':main()


