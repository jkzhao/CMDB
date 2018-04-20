# -*- coding: utf-8 -*-
import time

def cal_time(func):
    '''计算函数运行时间的装饰器'''
    def wrapper(*args, **kwargs):
        t1 = time.time()
        result = func(*args, **kwargs)
        t2 = time.time()
        print("%s running time: %s secs." % (func.__name__, t2-t1))
        return result
    return wrapper

