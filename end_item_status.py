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
        #print r.content
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
        pages=int(catinfo['totalResultsAvailable']) / int(catinfo['totalResultsReturned'])
        return pages+1
    def get_data(self,au):
        pages=self.get_pages(au.AuctionID)
        print au.AuctionItemUrl
        #itemd=self.get_item_detail(au)
        #pprint.pprint(itemd)
        #for i in range(1,pages+1):
        #    url=src
        #    d=self.__get_data_from_src(au.AuctionID,url,i)
        #    #print '='*50
        #    #pprint.pprint(d)
        #    #print au.AuctionItemUrl
        #    k=d['ResultSet']['Result']
        #    for j,p in enumerate(k):
        #        print '='*50
        #        print i,j+1
        #        pprint.pprint(p)

def get_end_item(mp):
    dnow=datetime.now()
    for i in mp.items.find({"Bids":{'$gt':30}}).sort([("EndTime",pymongo.ASCENDING)]).limit(3):
        ed=i['EndTime']
        gd=GetData(mp)
        ac=AucItem(i)
        gd.get_data(ac)
        #pprint.pprint(i)

def main():
    mp=MongoOp('localhost')
    get_end_item(mp)

if __name__=='__main__':main()
