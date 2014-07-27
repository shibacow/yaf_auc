#!/bin/bash
cd $(dirname $0);
python get_items.py 2>&1 | logger -p user.info

