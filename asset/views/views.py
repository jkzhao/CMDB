from django.shortcuts import render,redirect,HttpResponse
from django.views import View
from repository import models
from repository.models import UrlGroup,UrlInfor
from .account import auth

import json
from django.utils.decorators import method_decorator
from asset.service import asset
from django.http import JsonResponse
from asset.service.asset import Asset

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

    def delete(self, request):
        '''删除单个主机记录和批量删除主机记录'''
        response = Asset.delete_assets(request)

        # print(JsonResponse(response.__dict__))
        return JsonResponse(response.__dict__)
        # return redirect('/asset.html')

    def put(self, request):
        '''编辑主机'''
        response = Asset.put_assets(request)
        return JsonResponse(response.__dict__)


class AddAssetView(View):
    def get(self, request, *args, **kwargs):
        asset = Asset()
        ret = {}
        ret['idc_list'] = asset.idc_list
        ret['business_unit_list'] = asset.business_unit_list
        ret['device_type_list'] = asset.device_type_list
        ret['device_status_list'] = asset.device_status_list

        return render(request, 'add_asset.html', {'result': ret})

    def post(self, request):
        response = Asset.add_assets(request)
        return JsonResponse(response.__dict__)

class AddServerView(View):
    def get(self, request, *args, **kwargs):
        id = request.GET.get('id')
        # print(id)
        asset = Asset()
        response = asset.fetch_servers(id)

        return render(request, 'add_asset_server.html', {'response': response})

    def post(self, request):
        response = Asset.add_server(request)

        return JsonResponse(response.__dict__)


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

