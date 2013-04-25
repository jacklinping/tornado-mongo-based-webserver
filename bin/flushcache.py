#!/usr/bin/python
import os, sys

sys.path += [os.path.dirname(os.path.dirname(os.path.abspath(__file__)))]

from conf import config
from lib import cache

def flush_cache():
    c = cache.Cache(master=True)
    c.flush()

if __name__ == '__main__':
    flush_cache()

