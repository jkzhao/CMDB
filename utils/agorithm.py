#!/usr/bin/env python
# -*- coding:utf-8 -*-


def get_intersection(*args):
    '''
    获取所有set的交集
    :param args: set集合
    :return:交集列表
    '''
    base = args[0]
    result = base.intersection(*args)
    return list(result)


def get_exclude(total,part):
    '''
    获取所有set的差集: total中有的，而part中没有的
    :param total: set集合
    :param part:
    :return: 差集列表
    '''
    result = []
    for item in total:
        if item in part:
            pass
        else:
            result.append(item)
    return result

if __name__ == '__main__':
    client = {1, 3, 5, 9}
    db = {2, 4, 5, 9}
    print(get_intersection(client, db))
    print(get_exclude(client, db))
    print(client.difference(db))
