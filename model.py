#!/usr/bin/env python
# -*- coding:utf-8 -*-

from sqlalchemy import *
from sqlalchemy.orm import *

class CheckItem(object):
    def __init__(self,kw):
        pass

class TagJson(object):
    def __init__(self,json):
        self.json=json

class TagName(object):
    def __init__(self,name):
        self.name=name

class Tag(object):
    def __init__(self,dt,json,cnt):
        self.date=dt
        self.json=TagJson(json)
        self.tagcount=cnt

class TreeJson(object):
    def __init__(self,json):
        self.json=zlib.compress(json.encode('utf-8'))
    def _set_json(self,json):
        self._json=zlib.compress(json)
    def _get_json(self):
        return zlib.decompress(self._json)
    json=property(_get_json,_set_json)

class Tree(object):
    def __init__(self,tp,sz_w,sz_h,date,html):
        self.date=date
        self.size_type=unicode(tp)
        self.size_w=sz_w
        self.size_h=sz_h
        self.json=TreeJson(html)
def table_def(meta,delkey):
    clear_mappers()
    web.debug('calling table_def')
    check_items=Table(
        'check_items',meta,
        Column('id',String(255),primary_key=True),
        Column('AuctionID',Unicode(255),index=True,default=u"",nullable=False),
        Column('created_at',DateTime,default=func.now(),nullable=False),
        )

    #Index('tag_order',tag.c.date,tag.c.tag_name_id)
    #Index('tag_count',tag.c.date,tag.c.tagcount)

    def tbl_delete(delk,tbl):
        if isDel(delk) and tbl.exists():
            tbl.drop()

    def tbl_create(tbl):
        if not tbl.exists():
            tbl.create()

    tbllist=[
        ('deltagjson',tag_json),
        ('deltag',tag),
        ('deltagname',tag_name),
        ('deltreejson',tree_json),
        ('deltree',tree),
        ('delpoints',points),
        ('delheadline',headline),
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
    engine=create_engine(db_path,pool_size=100,pool_recycle=60,strategy='threadlocal',connect_args={'compress':True})
    meta=MetaData()
    meta.bind=engine
    meta.bind.echo=echoOn
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
    db_host='mysql://nicoran:nicoran@localhost/nr_tag_search?charset=utf8'
    meta=mkmetadata(db_host,echoOn=True)
    tbldel={
        'deltag':False,
        'deltagjson':False,
        'deltagname':False,
        'deltree':False,
        'deltreejson':False,
        'delpoints':False,
        }
    table_def(meta,tbldel)
    sess=mksession()

if __name__=='__main__':main()
