#!/usr/bin/env python
# -*- coding:utf-8 -*-
from io import BytesIO
from hashlib import sha1

from utils.check_code import create_validate_code

from django.views import View
from django.shortcuts import render,redirect,HttpResponse
from repository import models

from django.utils.decorators import method_decorator

def login(request):
    '''登录'''
    error_msg = ""
    if request.method == "GET":
        return render(request, 'login.html')
    elif request.method == "POST":
        code = request.POST.get('check_code')
        if code.upper() != request.session['CheckCode'].upper():
            error_msg = "验证码错误"
            return render(request, 'login.html', {'error_msg': error_msg})
        u = request.POST.get('user')
        p = request.POST.get('pwd')
        # obj = models.UserInfo.objects.filter(username=u,password=p).first()
        # print(obj)# obj None,
        # count = models.UserInfo.objects.filter(username=u, password=p).count()
        obj = models.AdminInfo.objects.filter(username=u).first()
        if not obj:
            error_msg = "用户名不存在"
            return render(request, 'login.html', {'error_msg': error_msg})
        passwd_sha1 = sha1()
        passwd_sha1.update(p.encode("utf-8"))
        user_passwd_sha1 = passwd_sha1.hexdigest()
        if obj.password == user_passwd_sha1:
            request.session['username'] = u
            request.session['is_login'] = True
            if request.POST.get('rememberMe', None) == '1':
                request.session.set_expiry(604800)

            if "login_from" not in request.session.keys():
                return redirect('/index.html')
            return redirect(request.session['login_from'])
        else:
            error_msg = "密码错误"
            return render(request, 'login.html', {'error_msg': error_msg})

def auth(func):
    '''FBV装饰器实现认证，防止多个url需要认证'''
    def inner(request, *args, **kwargs):
        if not request.session.get('username', None):
            # 记住来源的url，如果没有则设置为首页('/')
            # request.session['login_from'] = request.META.get('HTTP_REFERER', '/index.html')
            request.session['login_from'] = request.path
            print(request.session['login_from'])
            return redirect('/login.html')
        return func(request, *args, **kwargs)
    return inner

def check_code(request):
    """
    验证码
    :param request:
    :return:
    """
    stream = BytesIO()
    img, code = create_validate_code()
    img.save(stream, 'PNG') #'PNG'是生成文件的后缀名
    request.session['CheckCode'] = code

    return HttpResponse(stream.getvalue()) #从内存中读出来

class LogoutView(View):
    def get(self, request, *args, **kwargs):
        '''注销'''
        request.session.clear()
        return redirect('/login.html')
