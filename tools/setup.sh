#!/bin/sh
# Copyright 2017, Ryan P. Kelly. All Rights Reserved.

if [ ! -e virtualenv ]; then
    virtualenv virtualenv
fi

. virtualenv/bin/activate

python setup.py develop
