from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import HttpResponse
from django.views import View
from asset import models
from asset.models import UrlGroup,UrlInfor

import json
from utils import pagination
from io import BytesIO
from utils.check_code import create_validate_code
from hashlib import sha1


def check_code(request):
    """
    验证码
    :param request:
    :return:
    """
    # stream = BytesIO()
    # img, code = create_validate_code()
    # img.save(stream, 'PNG')
    # request.session['CheckCode'] = code
    # return HttpResponse(stream.getvalue())

    # 打开固定图片
    # data = open('static/imgs/avatar/20130809170025.png','rb').read()
    # return HttpResponse(data)

    # 1. 自己创建一张图片 pip3 install Pillow
    # 2. 在图片中写入随机字符串
    # obj = object()
    # 3. 将图片写入到指定文件
    # 4. 打开指定目录的该文件，读取内容
    # 5. HttpResponse(data)

    stream = BytesIO()
    img, code = create_validate_code()
    # print(img, code)
    # f = open('xxxxx.png', 'wb')
    # img.save(f, 'PNG')
    # f.close()
    # return HttpResponse(open('xxxxx.png', 'rb').read()) #这是写在文件中，在读出来，不如写在内存中，省写文件的时间了，更快
    img.save(stream, 'PNG') #'PNG'是生成文件的后缀名
    request.session['CheckCode'] = code
    return HttpResponse(stream.getvalue()) #从内存中读出来

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
        obj = models.User.objects.filter(username=u).first()
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
                return redirect('/index/')
            return redirect(request.session['login_from'])
        else:
            error_msg = "密码错误"
            return render(request, 'login.html', {'error_msg': error_msg})

def auth(func):
    '''FBV装饰器实现认证，防止多个url需要认证'''
    def inner(request, *args, **kwargs):
        if not request.session.get('username', None):
            # 记住来源的url，如果没有则设置为首页('/')
            # request.session['login_from'] = request.META.get('HTTP_REFERER', '/index/')
            request.session['login_from'] = request.path
            print(request.session['login_from'])
            return redirect('/login/')
        return func(request, *args, **kwargs)
    return inner

def logout(request):
    '''注销'''
    request.session.clear()
    return redirect('/login/')

'''
主页
'''
@auth
def index(request):
    '''主页'''
    return HttpResponse("ni hao...")

'''
主机管理
'''
@auth
def host(request):
    '''主机展示表和添加主机'''
    # HOSTS = models.Host.objects.all()  # 全局变量
    if request.method == "GET":
        # current_page = request.GET.get('p', 1)  # 如果p不存在，看第1页。每一页显示10个数据 [0-10],[10-20],[20-30]
        # current_page = int(current_page)  # GET获取到的都是字符串
        #
        # val = request.COOKIES.get('per_page_count', 10)  # 从Cookies中拿到当前用户要求一页显示多少数据，默认是10
        # val = int(val)
        # page_obj = pagination.Page(current_page, len(HOSTS), val)
        #
        # data = HOSTS[page_obj.start:page_obj.end]  # 取数据
        # data_length = len(data)
        # page_str = page_obj.page_str("/host/")
        #
        # b_list = models.Business.objects.all()  # 拿到业务线
        # e_list = models.EngineRoom.objects.all()  # 拿到机房
        # return render(request, "host.html",
        #               {"hosts": data, "data_length": data_length, "page_str": page_str, "b_list": b_list,
        #                "e_list": e_list, 'current_user': request.session['username']})

        hosts = models.Host.objects.all()
        return render(request, 'host.html', {"hosts": hosts, 'current_user': request.session['username']})
    elif request.method == "POST":
        result = {'status': True, 'error': None, 'data': None}
        try:  # 因为这里面的代码有可能出错
            h = request.POST.get('hostname')
            i = request.POST.get('ip')
            b = request.POST.get('b_id')
            e = request.POST.get('e_id')
            print(h)
            print(i)
            if h:
                pass
                if i and is_valid_ipv4_address(i):
                    # new_host = models.Host(hostname=h,ip=i,b_id=b,e_id=e)
                    # new_host.save() #这两句和下面那句等效
                    models.Host.objects.create(hostname=h,
                                               ip=i,
                                               b_id=b,
                                               e_id=e)
                else:
                    result['status'] = False
                    result['error'] = "IP地址格式有误"
            else:
                result['status'] = False
                result['error'] = "请输入主机名"
        except Exception as e:
            result['status'] = False
            result['error'] = '请求错误'

        return HttpResponse(json.dumps(result))  # ajax请求返回就写HttpResponse，HttpResponse()里面是字符串
        # 其实也是能用render()，一般要渲染一些东西返回给用户，但是前端拿到html，没有办法JSON.parse()，必须形似字典才行。
        # 但是不能用redirect()

def delete_host(request):
    '''删除单个主机记录和批量删除主机记录'''
    hid = request.POST.get('hid')
    # print(hid,type(hid)) #"["1","2"]"  "1,2"
    hid_list = hid.split(",")
    for hid in hid_list:
        #print(hid,type(hid))
        models.Host.objects.filter(id=hid).first().delete()

    return redirect('/host')

def edit_host(request):
    '''编辑主机'''
    hid = request.POST.get('hid')
    # print(hid)
    obj = models.Host.objects.filter(id=hid).first()
    result = {'status': True, 'error': None, 'data': None}
    try:  # 因为这里面的代码有可能出错
        h = request.POST.get('hostname')
        i = request.POST.get('ip')
        b = request.POST.get('b_id')
        e = request.POST.get('e_id')
        if h:
            pass
            if i and is_valid_ipv4_address(i): #更新
                obj.hostname = h
                obj.ip = i
                obj.b_id = b
                obj.e_id = e
                obj.save()
            else:
                result['status'] = False
                result['error'] = "IP地址格式有误"
        else:
            result['status'] = False
            result['error'] = "请输入主机名"
    except Exception as e:
        result['status'] = False
        result['error'] = '请求错误'

    return HttpResponse(json.dumps(result))


import socket
def is_valid_ipv4_address(address):
    '''验证ip地址格式是否正确'''
    try:
        socket.inet_pton(socket.AF_INET, address)
    except AttributeError:  # no inet_pton here, sorry
        try:
            socket.inet_aton(address)
        except socket.error:
            return False
        return address.count('.') == 3
    except socket.error:  # not a valid address
        return False

    return True



@auth
def environment(request):
    """
    构造数据格式
        list
            dict
                list
                    dict

    从组里取出所有组，然后再根据一对多的关系，通过组获取url的具体信息，属于反向获取数据
    [{
        "code": "utils",
        "list": [
            {"desc": "\u7ebf\u4e0aelk\u65e5\u5fd7\u68c0\u7d22\u7cfb\u7edf", "href": "http://192.168.0.210", "title": "\u7ebf\u4e0aelk\u7cfb\u7edf"},
            {"desc": "\u7ebf\u4e0a\u90ae\u7bb1\u5730\u5740\uff0c\u516c\u53f8\u5185\u90e8\u90ae\u7bb1\u767b\u9646\u94fe\u63a5", "href": "http://192.168.0.215", "title": "\u90ae\u7bb1\u5730\u5740"}
            ],
        "title": "\u751f\u4ea7\u73af\u5883"
    },
    ...]
    """
    _group_lists = UrlGroup.objects.all()
    _datas = []
    for group in _group_lists.all():
        if group.group_set.count() > 0:
            _group_template = {"title": "{0}".format(group.group_name), "code": "{0}".format(group.code), "list": []}
            _group = UrlGroup.objects.get(code=group.code)
            for k in _group.group_set.all():
                _url_template = {"title": "{0}".format(k.url_name), "href": "{0}".format(k.url_path),
                                 "desc": "{0}".format(k.url_desc)}
                _group_template["list"].extend([_url_template])
            _datas.extend([_group_template])

    # return HttpResponse(json.dumps(_datas))
    return render(request, 'environment.html', {'url_group_info': _datas, 'current_user': request.session['username']})

def software(request):
    """
    todo
    """
    return HttpResponse("开发中。。。")

def business(request):
    """
    todo
    """
    return HttpResponse("开发中。。。")

def user(request):
    """
    todo
    """
    return HttpResponse("开发中。。。")
