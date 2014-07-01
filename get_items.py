#!/usr/bin/env python
# -*- coding:utf-8 -*-

import yaml
import requests
import re
import simplejson
import pprint
from mongo_op import MongoOp
import time
from fluent import sender,event
from datetime import datetime
import copy
import logging
import logging.handlers

my_logger = logging.getLogger('MyLogger')
my_logger.setLevel(logging.DEBUG)
handler = logging.handlers.SysLogHandler(address = '/dev/log')
my_logger.addHandler(handler)

src = 'http://auctions.yahooapis.jp/AuctionWebService/V2/categoryLeaf'
conf=yaml.load(open('conf.yaml'))

class GetItems(object):
    TotalAccess=[0]
    def __init__(self,mp,cid,cinfo):
        self.mp=mp
        self.cid=cid
        self.cinfo=cinfo

    @classmethod
    def get_cat(cls,mp,depth):
        sums=0
        catlist=[]
        sums=sum([c['NumOfAuctions'] for c in mp.cat.find({"Depth":depth}) if 'NumOfAuctions' in c])
        for c in mp.cat.find({"Depth":depth}):
            if 'NumOfAuctions' in c:
                nums=c['NumOfAuctions']
                if 100.0*nums/sums>0.5:
                    catlist.append(c)
        return sorted(catlist,key=lambda x:x['NumOfAuctions'],reverse=True)
    def __get_data_from_src(self,cid,page):
        params=dict(output='json',
                    appid=conf['app_id'],
                    category=cid,
                    sort='bids',
                    page=page)
        url=src
        r=requests.get(url,params=params)
        self.TotalAccess[0]+=1
        #print r.content
        rs=re.search('^loaded\((.+)\)$',r.content)
        #print r.content
        if not rs:return
        a=rs.group(1)
        time.sleep(0.1)
        return simplejson.loads(a)

    def get_pages(self,cid):
        d=self.__get_data_from_src(cid,0)
        if not d:return 0
        catinfo=d['ResultSet']['@attributes']
        pages=int(catinfo['totalResultsAvailable']) / int(catinfo['totalResultsReturned'])
        return pages
    def __parse_time(self,tm):
        tm=tm.split('+')[0]
        return datetime.strptime(tm,'%Y-%m-%dT%H:%M:%S')
    def __save_td(self,k):
        for cd in ('EndTime','CreatedAt'):
            k[cd]=k[cd].strftime('%Y-%m-%d %H:%M:%S')
        event.Event('yaf_auc.items',k)
    def __save_mongo(self,k):
        self.mp.items_save(k)

    def get_items(self,cid,page):
        d=self.__get_data_from_src(cid,page)
        if not d:return 0
        bids=0        
        r=d['ResultSet']['Result']['Item']
        if isinstance(r,list):
            for k in r:
                k['EndTime']=self.__parse_time(k['EndTime'])
                k['CreatedAt']=datetime.now()
                k['CategoryId']=self.cid
                k['CategoryIdPath']=self.cinfo['CategoryIdPath']
                k=MongoOp.parse_data(k)
                bids=k['Bids']
                if bids>0:
                    self.__save_mongo(copy.deepcopy(k))
                    self.__save_td(copy.deepcopy(k))
                    msg="totalaccess={} bids={} page={} title={}".format(self.TotalAccess[0],bids,page,k['Title'].encode('utf-8'))
                    my_logger.info(msg)
        return bids
def main():
    sender.setup('td')
    totalsums=0
    mp=MongoOp('localhost')
    r=GetItems.get_cat(mp,3)
    for c in r:
        cid=c['CategoryId']
        msg="cid={} aucnum={} catpath={}".format(cid,c['NumOfAuctions'],c['CategoryPath'].encode('utf-8'))
        my_logger.info(msg)
        gi=GetItems(mp,cid,c)
        pages=gi.get_pages(cid)
        msg="pages={},totalaccess={}".format(pages,GetItems.TotalAccess)
        my_logger.info(msg)
        for i in range(1,pages):
            b=gi.get_items(cid,i)
            if b==0:
                msg="page {} break ,totalaccess={}".format(i,GetItems.TotalAccess)
                my_logger.debug(msg)
                break
if __name__=='__main__':main()
