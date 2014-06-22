#!/usr/bin/env python
# -*- coding:utf-8 -*-

from mongo_op import MongoOp
import pymongo
import pprint
from datetime import datetime

class AucItem(object):
    def __init__(self,i):
        self.i=i
        for k in i:
            v=i[k]
            setattr(self,k,v)
    def __repr__(self):
        i=self.i
        msg="id={} Bids={} Price={} endTime={} Title={} link={}".format(
            i['AuctionID'],i['Bids'],i['CurrentPrice'],i['EndTime'],i['Title'].encode('utf-8'),i['AuctionItemUrl']
        )
        return msg

def get_end_item(mp):
    dnow=datetime.now()
    for i in mp.items.find({"Bids":{'$gt':30}}).sort([("EndTime",pymongo.ASCENDING)]).limit(10):
        ed=i['EndTime']
        pprint.pprint(i)
        #ac=AucItem(i)
        #if ac.Bids>2:
        #print "="*30
        #print ac
def main():
    mp=MongoOp('localhost')
    get_end_item(mp)

if __name__=='__main__':main()
