#!/usr/bin/env python
# -*- coding:utf-8 -*-

from mongo_op import MongoOp
import pymongo
import pprint
import yaml
import requests
import re
import time
import simplejson
from datetime import datetime
conf=yaml.load(open('conf.yaml'))
src='http://auctions.yahooapis.jp/AuctionWebService/V1/BidHistoryDetail'
detail_src='http://auctions.yahooapis.jp/AuctionWebService/V2/auctionItem'

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

class BidsHistory(object):
    def __init__(self,au):
        self.info={}
        self.au=au
        

class GetData(object):
    TotalAccess=[0]
    def __init__(self,mp):
        self.mp=mp
    def __get_data_from_src(self,url,aid,page):
        params=dict(output='json',
                    appid=conf['app_id'],
                    auctionID=aid,
                    page=page
                    )
        r=requests.get(url,params=params)
        self.TotalAccess[0]+=1
        #print r.content
        rs=re.search('^loaded\((.+)\)$',r.content)
        if not rs:return
        a=rs.group(1)
        time.sleep(0.1)
        return simplejson.loads(a)
    def get_item_detail(self,au):
        url=detail_src
        return self.__get_data_from_src(url,au.AuctionID,1)
        
    def get_pages(self,aid):
        url=src
        d=self.__get_data_from_src(url,aid,0)
        if not d:return 0
        catinfo=d['ResultSet']['@attributes']
        tra=int(catinfo['totalResultsAvailable'])
        trr=int(catinfo['totalResultsReturned'])
        pages= tra/trr 
        if tra%trr>0:
            pages+=1
        return pages
    def get_data(self,au):
        pages=self.get_pages(au.AuctionID)
        bidslist=[]
        #pprint.pprint(au.i)
        aid=au.AuctionID
        for i in range(1,pages+1):
            url=src
            d=self.__get_data_from_src(url,aid,i)
            #pprint.pprint(d)
            k=d['ResultSet']['Result']
            for j,p in enumerate(k):
                #print '='*50
                #print i,j+1
                #pprint.pprint(p)
                bidslist.append(p)
        
        
def get_end_item(mp):
    dnow=datetime.now()
    cond=mp.items.find({"$and":[
        {"Bids":{'$gt':1}},\
        {"EndTime":{"$lt":datetime.now()}}\
    ]}).sort([("EndTime",pymongo.ASCENDING)])
    print cond.count()
    for i in cond.limit(3):
        ed=i['EndTime']
        gd=GetData(mp)
        ac=AucItem(i)
        print ac
        gd.get_data(ac)

def main():
    mp=MongoOp('localhost')
    get_end_item(mp)

if __name__=='__main__':main()
