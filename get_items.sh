#!/bin/bash
cd $(dirname $0);
./get_items.py 2>&1 | logger -p user.info

