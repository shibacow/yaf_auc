#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
sys.path.append('lib')
from mongo_op import MongoOp
import pymongo
import model
import pprint
import yaml
import requests
import re
import time
import simplejson
from datetime import datetime,timedelta
import logging
FORMAT="%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO,format=FORMAT)


conf=yaml.load(open('conf.yaml'))
src='http://auctions.yahooapis.jp/AuctionWebService/V1/BidHistoryDetail'
detail_src='http://auctions.yahooapis.jp/AuctionWebService/V2/auctionItem'
from common import time_profile

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
    def __init__(self,mp,sess):
        self.mp=mp
        self.sess=sess
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
        if not rs:return None
        a=rs.group(1)
        time.sleep(0.1)
        return simplejson.loads(a),r
    def __conv_data(self,bid):
        #pprint.pprint(bid)
        dt=bid['Date']
        dt=dt.strip()
        dt=dt.split('+')[0]
        dt=datetime.strptime(dt,'%Y-%m-%dT%H:%M:%S')
        bid['Date']=dt
        price=bid['Price']
        price=price.split('.')[0]
        bid['Price']=int(price)
    def get_item_detail(self,au):
        url=detail_src
        return self.__get_data_from_src(url,au.AuctionID,1)
        
    def get_pages(self,aid):
        url=src
        d,r=self.__get_data_from_src(url,aid,0)
        if not d:
            return 0
        if not 'ResultSet' in d:
            return 0
        catinfo=d['ResultSet']['@attributes']
        tra=int(catinfo['totalResultsAvailable'])
        trr=int(catinfo['totalResultsReturned'])
        if tra==0 and trr==0:
            logging.warning("tra={} trr={}".format(tra,trr))
            return 0
        pages= tra/trr 
        if tra%trr>0:
            pages+=1
        return pages
    def __more_detail_date(self,bidslist):
        bdlist=sorted(bidslist,key=lambda x:x['Date'])
        bfirst=bdlist[0]['Date']
        bend=bdlist[-1]['Date']
        bt=bend-bfirst
        btsize=bt.total_seconds()
        if btsize==0:
            return False
        #print "bfirst={} bend={} bdiff={}".format( bfirst,bend,bt)
        for bid in bidslist:
            dt=bid['Date']
            d0=dt-bfirst
            #print "bfirst={} dt={} d0={} dddf={}".format( bfirst,dt,d0,d0//bt)
            progress=d0.total_seconds() / btsize
            bid['FirstData']=bfirst
            bid['EDate']=bend
            bid['DateProgress']=progress
            #print progress
            
    def __more_price(self,bidslist):
        pdist=sorted(bidslist,key=lambda x:x['Price'])
        pfirst=pdist[0]['Price']
        pend=pdist[-1]['Price']
        pdiff=pend-pfirst
        if pdiff<=0:return False
        #print "pfirst={} pend={} pdiff={}".format(pfirst,pend,pdiff)
        for bid in bidslist:
            dt=bid['Price']
            diff=dt-pfirst
            progress=diff*1.0/pdiff
            ##print progress
            bid['FirstPrice']=pfirst
            bid['EPrice']=pend
            bid['PriceProgress']=progress
    def __conv_datetime(self,tm):
        tm=tm.split('+')[0]
        return datetime.strptime(tm,'%Y-%m-%dT%H:%M:%S')
    def __conv_int(self,tn):
        tn=tn.split('.')[0]
        return int(tn)

    def __item_info(self,au):
        d,response=self.get_item_detail(au)
        aucinfo=None
        if response.status_code == requests.codes.ok:
            if 'ResultSet' in d and 'Result' in d['ResultSet']:
                aucinfo=d['ResultSet']['Result']
                del aucinfo['Description']
                aucinfo['EndTime']=self.__conv_datetime(aucinfo['EndTime'])
                aucinfo['StartTime']=self.__conv_datetime(aucinfo['StartTime'])
                for k in ('Initprice','Price','Bids'):
                    aucinfo[k]=self.__conv_int(aucinfo[k])
        return aucinfo

    def get_data(self,au):
        aid=au.AuctionID
        print aid
        if self.mp.has_enditem(aid):
            logging.info("aid={} has saved".format(aid))
            return
        aucinfo=self.__item_info(au)
        if not aucinfo or aucinfo['EndTime']>(datetime.now()-timedelta(days=7)):
            if aucinfo and  'EndTime' in aucinfo:
                #pprint.pprint(aucinfo)
                logging.info("endtime={} aucid={}".format(aucinfo['EndTime'],aucinfo['AuctionID']))
            return 
        pages=self.get_pages(au.AuctionID)
        bidslist=[]
        for i in range(1,pages+1):
            url=src
            d,r=self.__get_data_from_src(url,aid,i)
            k=d['ResultSet']['Result']
            for j,p in enumerate(k):
                if not isinstance(p,dict):continue
                if 'Price' in p and 'Date' in p and p['IsCanceled']=='false':
                    self.__conv_data(p)
                    bidslist.append(p)
        if bidslist:
            if not self.__more_detail_date(bidslist) or not  self.__more_price(bidslist):
                bidslist=[]
        if bidslist:
            #pprint.pprint(aucinfo)
            aucinfo['bidslist']=bidslist
            if not self.mp.has_enditem(aid):
                self.mp.enditem_save(aucinfo)

def initdb(echoOn=False):
    meta=model.mkdbpath(conf['mysql'],echoOn=echoOn)
    tbldel={
        'delcheck_items':False
    }
    model.table_def(meta,tbldel)
    sess=model.mksession()
    return meta,sess

def init():
    mp=MongoOp('localhost')
    meta,sess=initdb(echoOn=True)
    return mp,meta,sess

@time_profile    
def collectEndItems(sess,mp):
    CI=model.CheckItem
    mx=model.func.max(CI.EndTime)
    mbids=model.func.max(CI.Bids)
    for a,etime,bids in sess.query(CI,mx,mbids).group_by(CI.AuctionID).having(mbids> 20).limit(20000).all():
        yield a,etime,bids
def main():
    mp,meta,sess=init()
    cnt=0
    bst=[]
    for a,etime,bids in collectEndItems(sess,mp):
        msg="{},{},{}\n".format(a.AuctionID,etime,bids)
        bst.append(msg)
        
        #print a,etime,bids
        #gd=GetData(mp,sess)
        #gd.get_data(a)
        #cnt+=1
        #msg="count={} total_access={}".format(cnt,GetData.TotalAccess[0])
        #logging.info(msg)
        #if GetData.TotalAccess[0]>20000:
        #    break
    out=open('end_list2.txt','wb')
    out.writelines(bst)
    out.close()
if __name__=='__main__':main()
