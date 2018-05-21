from django.shortcuts import render,redirect,HttpResponse
from django.views import View
from repository import models
from repository.models import UrlGroup,UrlInfor
from .account import auth

import json
from django.utils.decorators import method_decorator
from asset.service import asset
from django.http import JsonResponse

'''
资产管理
'''
@method_decorator(auth,name='dispatch')
class AssetView(View):
    def get(self, request, *args, **kwargs):
        obj = asset.Asset()
        response = obj.fetch_assets(request)
        # print(response.__dict__)
        # print(response.data)
        # print(JsonResponse(response.__dict__))
        return render(request, 'asset.html', {"response": response, 'current_user': request.session['username']})
        #return render(request, 'asset.html', {"assets": respone.data, 'current_user': request.session['username']})

    def post(self, request, *args, **kwargs):
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
        models.Asset.objects.filter(id=hid).first().delete()

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

class AssetDetailView(View):
    def get(self, request, device_type_id, asset_nid):
        # print("device_type_id", device_type_id)
        # print("asset_nid", asset_nid)
        response = asset.Asset.assets_detail(device_type_id, asset_nid)

        return render(request, 'asset_detail.html', {'response': response, 'device_type_id': device_type_id})

