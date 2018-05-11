# from django.db import models
#
# # Create your models here.
# class User(models.Model):
#     username = models.CharField('用户名', max_length=64, null=False, unique=True)
#     password = models.CharField('密码', max_length=60, null=False)
#     email = models.CharField('邮箱', max_length=60)
#     createtime = models.DateTimeField(auto_now_add=True, null=True)
#     updatetime = models.DateTimeField(auto_now=True, null=True)
#
#     class Meta:
#         verbose_name = '用户'
#         verbose_name_plural = '用户'
#
#     def __str__(self):
#         return self.username
#
# # 主机
# class Host(models.Model):
#     ip = models.GenericIPAddressField('IP地址', protocol="ipv4", db_index=True)
#     hostname = models.CharField('主机名', max_length=60, null=False)
#     createtime = models.DateTimeField(auto_now_add=True, null=True)
#     updatetime = models.DateTimeField(auto_now=True, null=True) #更新时间列，但是要想让django去更新这个字段，有条件：
#         # obj = UserGroup.objects.filter(id=1).update(caption='CEO') #这种更新，django不会去更新uptime列，必须使用下面3句话方式去更新，才会生效uptime列。
#         # obj = UserGroup.objects.filter(id=1).first()
#         # obj.caption = "CEO"
#         # obj.save()
#     b = models.ForeignKey(to="Business", to_field="id", verbose_name='所属业务线')
#     e = models.ForeignKey(to="EngineRoom", to_field="id", verbose_name='所属机房')
#
#     class Meta:
#         verbose_name = '主机'
#         verbose_name_plural = '主机'
#
#     def __str__(self):
#         return self.hostname
#
# # 业务线
# class Business(models.Model):
#     caption = models.CharField(verbose_name='业务线名称',max_length=32, null=False, unique=True)
#     code = models.CharField(verbose_name='业务线英文名', max_length=32, null=False, default="SA") #业务线英文简称
#     createtime = models.DateTimeField(auto_now_add=True, null=True)
#     updatetime = models.DateTimeField(auto_now=True, null=True)
#
#     class Meta:
#         verbose_name = '业务线'
#         verbose_name_plural = '业务线'
#
#     def __str__(self):
#         return self.caption
#
# # 机房
# class EngineRoom(models.Model):
#     name = models.CharField('机房名称', max_length=64, null=False, unique=True)
#     createtime = models.DateTimeField(auto_now_add=True, null=True)
#     updatetime = models.DateTimeField(auto_now=True, null=True)
#
#     class Meta:
#         verbose_name = '机房'
#         verbose_name_plural = '机房'
#
#     def __str__(self):
#         return self.name
#
# # 软件
# class Software(models.Model):
#     name = models.CharField('软件名称', max_length=32, null=False)
#     createtime = models.DateTimeField(auto_now_add=True, null=True)
#     updatetime = models.DateTimeField(auto_now=True, null=True)
#     r = models.ManyToManyField("Host",verbose_name='所属主机')
#
#     class Meta:
#         verbose_name = '软件'
#         verbose_name_plural = '软件'
#
#     def __str__(self):
#         return self.name
#
# # 环境组
# class UrlGroup(models.Model):
#     """
#     定义导航项目的组
#     """
#     group_name = models.CharField('分类名称', max_length=100, unique=True)
#     code = models.CharField('标签名称', max_length=100)
#     createtime = models.DateTimeField(auto_now_add=True, null=True)
#     updatetime = models.DateTimeField(auto_now=True, null=True)
#
#     class Meta:
#         verbose_name = '导航分组'
#         verbose_name_plural = '导航分组'
#
#     def __str__(self):
#         return self.group_name
#
# # 组内环境具体信息
# class UrlInfor(models.Model):
#     """
#     定义导航项目的具体信息
#     """
#     url_name = models.CharField('链接名称', max_length=100)
#     url_path = models.CharField('链接', max_length=200)
#     url_desc = models.TextField('链接描述', max_length=200)
#     url_group = models.ForeignKey(to=UrlGroup, verbose_name='分类名称', related_name='group_set', to_field="id")
#     createtime = models.DateTimeField(auto_now_add=True, null=True)
#     updatetime = models.DateTimeField(auto_now=True, null=True)
#
#     class Meta:
#         verbose_name = '导航详情'
#         verbose_name_plural = '导航详情'
#         ordering = ['url_name']
#
#     def __str__(self):
#         return self.url_name
#
