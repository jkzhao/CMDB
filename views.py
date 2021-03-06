from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import HttpResponse
from django.views import View
from asset import models

import json
from utils import pagination


def login(request):
    '''登录'''
    error_msg = ""
    if request.method == "GET":
        return render(request, 'login.html')
    elif request.method == "POST":
        u = request.POST.get('user')
        p = request.POST.get('pwd')
        # obj = models.UserInfo.objects.filter(username=u,password=p).first()
        # print(obj)# obj None,
        # count = models.UserInfo.objects.filter(username=u, password=p).count()
        obj = models.User.objects.filter(username=u).first()
        if not obj:
            error_msg = "用户名不存在"
            return render(request, 'login.html', {'error_msg': error_msg})
        if obj.password == p:
            request.session['username'] = u
            request.session['is_login'] = True
            if request.POST.get('rememberMe', None) == '1':
                request.session.set_expiry(604800)
            # print(request.path_info)
            return redirect('/host/')
        else:
            error_msg = "密码错误"
            return render(request, 'login.html', {'error_msg': error_msg})

def auth(func):
    '''FBV装饰器实现认证，防止多个url需要认证'''
    def inner(request, *args, **kwargs):
        if not request.session.get('username', None):
            return redirect('/login/')
        return func(request, *args, **kwargs)
    return inner

def logout(request):
    '''注销'''
    request.session.clear()
    return redirect('/login/')


def index(request):
    '''主页'''
    pass

'''
主机管理
'''
@auth
def host(request):
    '''主机展示表和添加主机'''
    HOSTS = models.Host.objects.all()  # 全局变量
    if request.method == "GET":
        current_page = request.GET.get('p', 1)  # 如果p不存在，看第1页。每一页显示10个数据 [0-10],[10-20],[20-30]
        current_page = int(current_page)  # GET获取到的都是字符串

        val = request.COOKIES.get('per_page_count', 10)  # 从Cookies中拿到当前用户要求一页显示多少数据，默认是10
        val = int(val)
        page_obj = pagination.Page(current_page, len(HOSTS), val)

        data = HOSTS[page_obj.start:page_obj.end]  # 取数据
        data_length = len(data)
        page_str = page_obj.page_str("/host/")

        b_list = models.Business.objects.all()  # 拿到业务线
        e_list = models.EngineRoom.objects.all()  # 拿到机房
        return render(request, "host.html",
                      {"hosts": data, "data_length": data_length, "page_str": page_str, "b_list": b_list,
                       "e_list": e_list, 'current_user': request.session['username']})
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


def insert(request):
    '''临时用来插入数据'''
    # models.EngineRoom.objects.create(name='阿里云')
    # models.EngineRoom.objects.create(name='金智园区4L')

    # models.Business.objects.create(caption='日志系统',code='logSystem')
    # models.Business.objects.create(caption='智能问答',code='robot')

    models.Host.objects.create(ip='172.16.206.16', hostname='hadoop16', b_id=1, e_id=2)
    models.Host.objects.create(ip='172.16.206.17', hostname='spark17', b_id=1, e_id=2)

    # models.User.objects.create(username='admin',password='123456',email='01115004@wisedu.com')

    return HttpResponse('OK')

