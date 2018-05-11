# -*- coding: utf-8 -*-

#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json
from django.db.models import Q
from repository import models
from utils.response import BaseResponse
from django.http.request import QueryDict

class Asset(object):
    extra_select = {
        'server_title': 'select hostname from repository_server where repository_server.asset_id=repository_asset.id and repository_asset.device_type_id=1',
        'network_title': 'select management_ip from repository_networkdevice where repository_networkdevice.asset_id=repository_asset.id and repository_asset.device_type_id=2',
    }

    @property
    def device_status_list(self):
        result = map(lambda x: {'id': x[0], 'name': x[1]}, models.Asset.device_status_choices) #Python 2.x 返回列表。
                                                                                                # Python 3.x 返回迭代器。
        return list(result) #<class 'list'>: [{'id': 1, 'name': '上架'}, {'id': 2, 'name': '在线'}, {'id': 3, 'name': '离线'}, {'id': 4, 'name': '下架'}]

    @property
    def device_type_list(self):
        result = map(lambda x: {'id': x[0], 'name': x[1]}, models.Asset.device_type_choices)
        return list(result) #<class 'list'>: [{'id': 1, 'name': '服务器'}, {'id': 2, 'name': '交换机'}, {'id': 3, 'name': '防火墙'}]

    @property
    def idc_list(self):
        values = models.IDC.objects.only('id', 'name', 'floor')
        result = map(lambda x: {'id': x.id, 'name': "%s-%s" % (x.name, x.floor)}, values)
        return list(result) #<class 'list'>: [{'id': 1, 'name': '兆维-1'}, {'id': 2, 'name': '石家庄-5'}, {'id': 3, 'name': '鹿泉-5'}]

    @property
    def business_unit_list(self):
        values = models.BusinessUnit.objects.values('id', 'name')
        return list(values) #<class 'list'>: [{'id': 2, 'name': '二手车'}, {'id': 3, 'name': '咨询'}, {'id': 1, 'name': '车商城'}]

    def fetch_assets(self, request):
        response = BaseResponse()
        try:
            ret = {}
            asset_list = models.Asset.objects.all().extra(select=self.extra_select).values()
            print("asset_list: %s" % asset_list)
            for ast in asset_list:
                print(type(ast))
                for device_status in self.device_status_list:
                    if ast.get('device_status_id') == device_status.get('id'):
                        ast['device_status'] = device_status.get('name')
                        break
                for device_type in self.device_type_list:
                    if ast.get('device_type_id') == device_type.get('id'):
                        ast['device_type'] = device_type.get('name')
                        break
                for idc in self.idc_list:
                    if ast.get('idc_id') == idc.get('id'):
                        ast['idc'] = idc.get('name')
                        break
                for business in self.business_unit_list:
                    if ast.get('business_unit_id') == business.get('id'):
                        ast['business_unit'] = business.get('name')
                        break

            ret['data_list'] = list(asset_list) #<class 'list'>: [{'network_title': None, 'cabinet_order': '1sfd', 'idc_id': 2, 'device_status_id': 1, 'business_unit_id': 3, 'cabinet_num': '11sdf', 'device_type_id': 1, 'server_title': 'c1.com', 'business_unit__name': '咨询', 'id': 5}]
            ret['global_dict'] = {
                'device_status_list': self.device_status_list,
                'device_type_list': self.device_type_list,
                'idc_list': self.idc_list,
                'business_unit_list': self.business_unit_list
            }    #{'business_unit_list': [{'id': 2, 'name': '二手车'}, {'id': 3, 'name': '咨询'}, {'id': 1, 'name': '车商城'}], 'idc_list': [{'id': 1, 'name': '兆维-1'}, {'id': 2, 'name': '石家庄-5'}, {'id': 3, 'name': '鹿泉-5'}], 'device_status_list': [{'id': 1, 'name': '上架'}, {'id': 2, 'name': '在线'}, {'id': 3, 'name': '离线'}, {'id': 4, 'name': '下架'}], 'device_type_list': [{'id': 1, 'name': '服务器'}, {'id': 2, 'name': '交换机'}, {'id': 3, 'name': '防火墙'}]}
            response.data = ret
            response.message = '获取成功'
        except Exception as e:
            response.status = False
            response.message = str(e)

        return response

    @staticmethod
    def delete_assets(request):
        response = BaseResponse()
        try:
            delete_dict = QueryDict(request.body, encoding='utf-8')
            id_list = delete_dict.getlist('id_list')
            models.Asset.objects.filter(id__in=id_list).delete()
            response.message = '删除成功'
        except Exception as e:
            response.status = False
            response.message = str(e)
        return response

    @staticmethod
    def put_assets(request):
        response = BaseResponse()
        try:
            response.error = []
            put_dict = QueryDict(request.body, encoding='utf-8')
            update_list = json.loads(put_dict.get('update_list'))
            error_count = 0
            for row_dict in update_list:
                nid = row_dict.pop('nid')
                num = row_dict.pop('num')
                try:
                    models.Asset.objects.filter(id=nid).update(**row_dict)
                except Exception as e:
                    response.error.append({'num': num, 'message': str(e)})
                    response.status = False
                    error_count += 1
            if error_count:
                response.message = '共%s条,失败%s条' % (len(update_list), error_count,)
            else:
                response.message = '更新成功'
        except Exception as e:
            response.status = False
            response.message = str(e)
        return response

    @staticmethod
    def assets_detail(device_type_id, asset_id):
        response = BaseResponse()
        try:
            if device_type_id == '1':
                response.data = models.Server.objects.filter(asset_id=asset_id).select_related('asset').first() #表之间进行join连表操作，一次性获取关联的数据
                                                                                                            #model.tb.objects.all().select_related('外键字段')
                print(response.data)
            else:
                response.data = models.NetworkDevice.objects.filter(asset_id=asset_id).select_related('asset').first()

        except Exception as e:
            response.status = False
            response.message = str(e)
        return response



