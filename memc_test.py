#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
sys.path.append('./lib')
from mongo_op import MongoOp
import MeCab
from pprint import pprint
import unicodedata

def main():
    mp=MongoOp('localhost')
    tagger=MeCab.Tagger()
    for i in mp.items.find().limit(100):
        print "="*30
        title=i['Title']
        title=unicodedata.normalize('NFKC',title)
        print title
        node=tagger.parseToNode(title.encode('utf-8'))
        while node:
            #pprint(node)
            print node.surface
            node=node.next

if __name__=='__main__':main()
