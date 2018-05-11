#!/usr/bin/env python
# -*- coding:utf-8 -*-
import time
import hashlib
from CMDB.settings import ASSET_AUTH_HEADER_NAME
from CMDB.settings import ASSET_AUTH_KEY
from CMDB.settings import ASSET_AUTH_TIME
from django.http import JsonResponse

# 已经访问过的列表
ENCRYPT_LIST = [
    # {'encrypt': encrypt, 'time': timestamp} #可以用redis实现超时时间
]


def api_auth_method(request):
    auth_key = request.META.get('HTTP_AUTHKEY')
    if not auth_key:
        return False
    sp = auth_key.split('|')
    if len(sp) != 2:
        return False
    encrypt, timestamp = sp
    timestamp = float(timestamp)
    limit_timestamp = time.time() - ASSET_AUTH_TIME #有效时间节点，比如是5点，那么客户端带来的时间戳只要小于5点的全是假的，直接拒绝
    print(limit_timestamp, timestamp)
    # 时间是否超时
    if limit_timestamp > timestamp:
        return False
    # 验证
    ha = hashlib.md5(ASSET_AUTH_KEY.encode('utf-8'))
    ha.update(bytes("%s|%f" % (ASSET_AUTH_KEY, timestamp), encoding='utf-8'))
    result = ha.hexdigest()
    print(result, encrypt)
    if encrypt != result:
        return False

    # 检查是否列表中已经存在，对已经失效的元素进行清除
    exist = False
    del_keys = []
    for k, v in enumerate(ENCRYPT_LIST):
        print(k, v)
        m = v['time']
        n = v['encrypt']
        if m < limit_timestamp:  #时间小于这个有效时间节点的，全部需要清除
            del_keys.append(k)
            continue
        if n == encrypt: #已经用过的url，还来访问，直接拒绝
            exist = True
    for k in del_keys:
        del ENCRYPT_LIST[k]

    if exist:
        return False
    ENCRYPT_LIST.append({'encrypt': encrypt, 'time': timestamp})
    return True


def api_auth(func):
    def inner(request, *args, **kwargs):
        if not api_auth_method(request):
            return JsonResponse({'code': 1001, 'message': 'API授权失败'}, json_dumps_params={'ensure_ascii': False})
        return func(request, *args, **kwargs)

    return inner
