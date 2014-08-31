#!/usr/bin/env python
# -*- coding:utf-8 -*-

from pymongo import MongoClient
import re

class MongoOp(object):
    def __init__(self,host):
        self.client=MongoClient(host)
        self.db=self.client.yaf_auc
        self.cat=self.db.cat
        self.items=self.db.items
        self.enditem=self.db.enditem
        self.enditemseed=self.db.enditemseed

    @classmethod
    def parse_data(cls,d):
        for k in d:
            v=d[k]
            if isinstance(v,basestring) and v.lower()=='true':
                d[k]=True
            if isinstance(v,basestring) and v.lower()=='false':
                d[k]=False
            if isinstance(v,basestring) and v.isdigit():
                v=int(v)
                d[k]=v
            if isinstance(v,basestring) and re.search('^[0-9.]*$',v):
                v=float(v)
                d[k]=v
            if isinstance(v,dict):
                d[k]=MongoOp.parse_data(v)
        return d
    def cat_save(self,d):
        if 'CategoryId' in d:
            catid=d['CategoryId']
            a=self.cat.find_one({'CategoryId':catid})
            if a:
                for k in d:
                    a[k]=d[k]
                self.cat.save(a)
            else:
                self.cat.insert(d)
    def items_save(self,d):
        if d:
            self.items.insert(d)
    def has_enditem(self,key,aid):
        return self.db[key].find_one({'AuctionID':aid})
    def enditem_save(self,key,d):
        if d:
            self.db[key].insert(d)

def main():
    mp=MongoOp('localhost')
    print mp

if __name__=='__main__':main()
