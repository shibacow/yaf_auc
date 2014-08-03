#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
sys.path.append('lib')
import model
import yaml
import pprint
from mongo_op import MongoOp
import logging
FORMAT="%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.DEBUG,format=FORMAT)

conf=yaml.load(open('conf.yaml'))

def get_items(mp):
    for i,item in enumerate(mp.items.find()):
        yield i,item

def get_end_items(mp,meta,sess):
    kw=('id','AuctionID','Title','CreatedAt','EndTime','Bids',\
        'CategoryId','CurrentPrice','CategoryIdPath','ItemUrl',\
        'BidOrBuy','SellerId','AuctionItemUrl')
    CI=model.CheckItem
    for i,item in get_items(mp):
        #for c in item:
        #    logging.info(c)
        if not isinstance(item['Title'],unicode):
            logging.info(item["Title"])
            logging.info(item['ItemUrl'])
            item['Title']=unicode(str(item['Title']),'utf-8')
        iid=item['_id']
        seller=item['Seller']['Id']
        item['SellerId']=seller
        if not sess.query(CI).filter(CI.id==iid).first():
            item['id']=iid
            ci=CI(item,kw)
            sess.add(ci)
        if i%10000==0:
            logging.info(i)
            sess.commit()
        #if i>100:
        #    break
    sess.commit()
            
def initdb():
    meta=model.mkdbpath(conf['mysql'],echoOn=False)
    tbldel={
        'delcheck_items':False
    }
    model.table_def(meta,tbldel)
    sess=model.mksession()
    return meta,sess

def main():
    mp=MongoOp('localhost')
    meta,sess=initdb()
    get_end_items(mp,meta,sess)
if __name__=='__main__':main()
