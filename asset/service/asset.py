# -*- coding: utf-8 -*-

#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json
from django.db.models import Q
from repository import models
from utils.response import BaseResponse
from django.http.request import QueryDict
from django.http import QueryDict

class Asset(object):
    asset_extra_select = {
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
        """获取资产"""
        response = BaseResponse()
        try:
            ret = {}
            asset_list = models.Asset.objects.all().extra(select=self.asset_extra_select).values()
            # print("asset_list: %s" % asset_list)
            for ast in asset_list:
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

    def fetch_servers(self, id):
        """获取服务器资产"""
        response = BaseResponse()
        try:
            asset = models.Asset.objects.filter(id=id)

            response.data = asset
            response.message = '获取成功'
        except Exception as e:
            response.status = False
            response.message = str(e)

        return response

    @staticmethod
    def delete_assets(request):
        """删除资产"""
        response = BaseResponse()
        try:
            # hid = request.body.get('hid')
            delete_dict = QueryDict(request.body)
            hid = delete_dict.get('hid')
            print(hid, type(hid))  # "["1","2"]"  "1,2"
            hid_list = hid.split(",")
            models.Asset.objects.filter(id__in=hid_list).delete()
            response.message = '删除成功'
        except Exception as e:
            response.status = False
            response.message = str(e)
        return response

    @staticmethod
    def add_assets(request):
        """添加资产"""
        response = BaseResponse()
        row_dict = {}
        try:
            add_dict = QueryDict(request.body)
            row_dict['device_type_id'] = add_dict.get('asset_type')
            row_dict['device_status_id'] = add_dict.get('asset_status')
            row_dict['cabinet_num'] = add_dict.get('cabinet_num')
            row_dict['cabinet_order'] = add_dict.get('cabinet_order')
            row_dict['idc_id'] = add_dict.get('idc')
            row_dict['business_unit_id'] = add_dict.get('business_unit')
            # row_dict['tag_id'] = add_dict.get('tag')
            latest_date_time = add_dict.get('latest_date')
            row_dict['latest_date'] = latest_date_time.split()[0]

            obj = models.Asset.objects.create(**row_dict)
            response.message = '添加成功'
            response.data = obj.id
        except Exception as e:
            response.status = False
            response.message = str(e)
        return response

    @staticmethod
    def add_server(request):
        """添加服务器"""
        response = BaseResponse()
        row_dict = {}
        try:
            add_dict = QueryDict(request.body)
            row_dict['asset_id'] = add_dict.get('asset')
            hostname = add_dict.get('hostname')
            hostname_list = models.Server.objects.all().values_list('hostname', flat=True)

            if hostname in hostname_list:
                response.status = False
                response.message = '主机名重复，请重新输入主机名'
            else:
                row_dict['hostname'] = hostname
                models.Server.objects.create(**row_dict)
                response.message = '添加成功'
        except Exception as e:
            response.status = False
            response.message = str(e)
        return response

    @staticmethod
    def put_assets(request):
        """修改资产"""
        response = BaseResponse()
        try:
            row_dict = {}
            put_dict = QueryDict(request.body, encoding='utf-8')
            hid = put_dict.get('hid')
            #方式一
            # cabinet_num = put_dict.get('cabinet_num')
            # cabinet_order = put_dict.get('cabinet_order')
            # b_id = put_dict.get('b_id')
            # e_id = put_dict.get('e_id')
            # asset_status_id = put_dict.get('asset_status_id')

            # obj = models.Asset.objects.filter(id=hid).first()
            # obj.cabinet_num = cabinet_num
            # obj.cabinet_order = cabinet_order
            # obj.business_unit_id = b_id
            # obj.idc_id = e_id
            # obj.device_status_id = asset_status_id
            # obj.save()

            #方式二
            row_dict['cabinet_num'] = put_dict.get('cabinet_num')
            row_dict['cabinet_order'] = put_dict.get('cabinet_order')
            row_dict['business_unit_id'] = put_dict.get('b_id')
            row_dict['idc_id'] = put_dict.get('e_id')
            row_dict['device_status_id'] = put_dict.get('asset_status_id')
            models.Asset.objects.filter(id=hid).update(**row_dict)

            response.message = '更新成功'
        except Exception as e:
            response.status = False
            response.message = str(e)
        return response

    @staticmethod
    def assets_detail(device_type_id, asset_id):
        """资产详细信息"""
        response = BaseResponse()
        try:
            if device_type_id == '1':
                response.data = models.Server.objects.filter(asset_id=asset_id).select_related('asset').first() #表之间进行join连表操作，一次性获取关联的数据
                                                                                                            #model.tb.objects.all().select_related('外键字段')
                # print(response.data)
            else:
                response.data = models.NetworkDevice.objects.filter(asset_id=asset_id).select_related('asset').first()

        except Exception as e:
            response.status = False
            response.message = str(e)
        return response



