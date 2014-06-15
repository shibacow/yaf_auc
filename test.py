#!/usr/bin/env python
# -*- coding:utf-8 -*-
import yaml
import requests
import re
import simplejson
import pprint
src='http://auctions.yahooapis.jp/AuctionWebService/V2/categoryTree'
import time
conf=yaml.load(open('conf.yaml'))

def parse(d):
    result=d['ResultSet']['Result']
    if not 'ChildCategory' in result:
        return
    for c in result['ChildCategory']:
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
        geturls(src,params)
        
def geturls(url,params):
    r=requests.get(url,params=params)
    rs=re.search('^loaded\((.+)\)$',r.content)
    a=rs.group(1)
    d=simplejson.loads(a)
    #pprint.pprint(d)
    time.sleep(0.1)
    parse(d)
def main():
    params=dict(output='json',
                category=26146,
                adf=1,
                appid=conf['app_id'])
    print params
    geturls(src,params)
if __name__=='__main__':main()
