#!/usr/bin/env python
# -*- coding:utf-8 -*-

from sqlalchemy import *
from sqlalchemy.orm import *
import web

class CheckItem(object):
    def __init__(self,item,kw):
        for k in kw:
            if k in item:
                v=item[k]
                setattr(self,k,v)

def table_def(meta,delkey):
    clear_mappers()
    web.debug('calling table_def')
    check_items=Table(
        'check_items',meta,
        Column('id',String(255),primary_key=True),
        Column('AuctionID',String(255),index=True,default=u"",nullable=False),
        Column('SellerId',String(255),index=True,default=u"",nullable=False),
        Column('Title',Unicode(255),index=True,default=u"",nullable=False),
        Column('CreatedAt',DateTime,default=func.now(),nullable=False),
        Column('EndTime',DateTime,default=func.now(),nullable=False),
        Column('Bids',Integer,index=True,nullable=False),
        Column('CategoryId',Integer,index=True,nullable=False),
        Column('CurrentPrice',Integer,index=True,nullable=False),
        Column('BidOrBuy',Integer,index=True,nullable=True),
        Column('CategoryIdPath',String(255),index=True,nullable=False),
        Column('ItemUrl',String(255),index=True,nullable=False),
        Column('InsertedAt',DateTime,default=func.now(),nullable=False),
        )
    mapper(CheckItem,check_items)
    #Index('tag_order',tag.c.date,tag.c.tag_name_id)
    #Index('tag_count',tag.c.date,tag.c.tagcount)

    def isDel(attr):
        if attr in delkey and delkey[attr]==True:
            return True
        else:
            return False

    def tbl_delete(delk,tbl):
        if isDel(delk) and tbl.exists():
            tbl.drop()

    def tbl_create(tbl):
        if not tbl.exists():
            tbl.create()

    tbllist=[
        ('delcheck_items',check_items),
        ]
    '''
    テーブルの作成と、削除で依存関係のため順序が逆なので、
    createとdeleteで、順序を逆順にする。
    '''
    for (k,tbl) in tbllist:
        tbl_delete(k,tbl)
    tbllist.reverse()
    for (k,tbl) in tbllist:
        tbl_create(tbl)

def mkmetadata(db_path,echoOn=False):
    #engine=create_engine(db_path,pool_size=100,pool_recycle=60,strategy='threadlocal',connect_args={'compress':True})
    engine=create_engine(db_path,echo=echoOn)
    meta=MetaData()
    meta.bind=engine
    return meta
def mkdbpath(d,echoOn=False):
    db_host='%s://%s:%s@%s/%s?charset=utf8' %\
        (d['dbtype'],d['username'],d['password'],d['host'],d['domain'])
    meta=mkmetadata(db_host,echoOn)
    return meta

def mksession(bind=None):
    return scoped_session(sessionmaker(bind=bind))

def readjson(f):
    return simplejson.load(f)

def main():
    db_host='mysql://yaf_auc:yaf_auc@localhost/yaf_auc?charset=utf8'
    #db_host='sqlite:///:memory:'
    meta=mkmetadata(db_host,echoOn=True)
    tbldel={
        'delcheck_items',True,
        }
    table_def(meta,tbldel)
    sess=mksession()

if __name__=='__main__':main()
