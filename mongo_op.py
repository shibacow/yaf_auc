#!/usr/bin/env python
# -*- coding:utf-8 -*-

from pymongo import MongoClient

class MongoOp(object):
    def __init__(self,host):
        self.client=MongoClient(host)
        self.db=self.client.yaf_auc
        self.cat=self.db.cat
    def __parse_int(self,d):
        for k in d:
            v=d[k]
            if v.lower()=='true':
                d[k]=True
            if v.lower()=='false':
                d[k]=False
            if v.isdigit():
                v=int(v)
                d[k]=v

        return d
    def save(self,d):
        d=self.__parse_int(d)
        if 'CategoryId' in d:
            catid=d['CategoryId']
            a=self.cat.find_one({'CategoryId':catid})
            if a:
                for k in d:
                    a[k]=d[k]
                self.cat.save(a)
            else:
                self.cat.insert(d)

def main():
    mp=MongoOp('localhost')
    print mp

if __name__=='__main__':main()
