#!/bin/bash
cd $(dirname $0);
date=`date +%Y-%m-%d`
echo "start"  >> /tmp/"$date".log 2>&1
./end_item_status.py >> /tmp/"$date".log 2>&1
echo "end"  >> /tmp/"$date".log 2>&1

