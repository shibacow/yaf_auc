#!/usr/bin/env python
# -*- coding:utf-8 -*-

from pymongo import MongoClient
import yaml
import requests

src = 'http://auctions.yahooapis.jp/AuctionWebService/V2/categoryLeaf'
conf=yaml.load(open('conf.yaml'))

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

def sumofnum(mp):
    sm=sum([c['NumOfAuctions'] for c in mp.cat.find({"IsLeaf":True}) if 'NumOfAuctions' in c])
    print sm
def show_cat(mp):
    sums=0
    sums=sum([c['NumOfAuctions'] for c in mp.cat.find({"Depth":2}) if 'NumOfAuctions' in c])
    print sums
    for c in mp.cat.find({"Depth":2}):
        if 'NumOfAuctions' in c:
            nums=c['NumOfAuctions']
            if 100.0*nums/sums>1.0:
                print c['CategoryId'],c['CategoryPath'],'|',nums,'|',(1.0*nums)/sums
        else:
            pass
            #print 'NotNums',c['CategoryPath']

#def get_category_leaf(mp,rootcid):
def get_items(cid):
    params=dict(output='json',
                appid=conf['app_id'],
                category=cid)
    url=src
    r=requests.get(url,params=params)
    print r.content
def main():
    mp=MongoOp('localhost')
    #sumofnum(mp)
    #show_cat(mp)
    get_items(27727)
if __name__=='__main__':main()
