#!/usr/bin/env python
# -*- coding:utf-8 -*-
import yaml
import requests
import re
import simplejson
import pprint
src='http://auctions.yahooapis.jp/AuctionWebService/V2/categoryTree'
import time
import mongo_op
conf=yaml.load(open('conf.yaml'))

def parse(d,mp):
    result=d['ResultSet']['Result']
    if not 'ChildCategory' in result:
        return
    for c in result['ChildCategory']:
        mp.save(c)
        print c['CategoryId'],c['CategoryName'].encode('utf-8'),c['Depth'],c['IsLeaf'],
        if 'NumOfAuctions' in c:
            print c['NumOfAuctions']
        else:
            print 'Num Of Auctions is None'
        print '\t',c['CategoryPath'].encode('utf-8'),c['CategoryIdPath']
        #print '\t\t',c
        params=dict(output='json',
                    category=c['CategoryId'],
                    adf=1,
                    appid=conf['app_id'])
        geturls(src,params,mp)
    
def geturls(url,params,mp):
    try:
        r=requests.get(url,params=params)
        rs=re.search('^loaded\((.+)\)$',r.content)
        a=rs.group(1)
        d=simplejson.loads(a)
        #pprint.pprint(d)
        time.sleep(0.1)
        parse(d,mp)
    except requests.exceptions.ChunkedEncodingError,err:
        print err
def main():
    params=dict(output='json',
                category=0,
                adf=1,
                appid=conf['app_id'])
    print params
    mp=mongo_op.MongoOp('localhost')
    geturls(src,params,mp)
if __name__=='__main__':main()
