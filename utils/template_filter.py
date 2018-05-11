# -*- coding: utf-8 -*-

from django import template

register = template.Library() #生成一个注册器

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)