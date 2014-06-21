#!/usr/bin/env python
# -*- coding:utf-8 -*-

import yaml
import requests
import re
import simplejson
import pprint

src = 'http://auctions.yahooapis.jp/AuctionWebService/V2/categoryLeaf'
conf=yaml.load(open('conf.yaml'))

def get_items(cid):
    params=dict(output='json',
                appid=conf['app_id'],
                category=cid,
                page=3)
    url=src
    r=requests.get(url,params=params)
    #print r.content
    rs=re.search('^loaded\((.+)\)$',r.content)
    #print r.content
    if not rs:return
    a=rs.group(1)
    d=simplejson.loads(a)
    r=d['ResultSet']['Result']['Item']
    catinfo=d['ResultSet']['@attributes']
    print catinfo
    pages=int(catinfo['totalResultsAvailable']) / int(catinfo['totalResultsReturned'])
    print pages
    #print len(r)
    #for k in r:
    #    pprint.pprint(k)
def main():
    get_items(27727)
if __name__=='__main__':main()
