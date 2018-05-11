from django.db import models

# Create your models here.
from django.db import models


class UserProfile(models.Model):
    """
    用户信息表：存着很多用户，如果只有两个人可以登录，就只给这两个人设置用户名密码，见下面那张表
    """
    name = models.CharField(u'姓名', max_length=32)
    email = models.EmailField(u'邮箱')
    phone = models.CharField(u'座机', max_length=32, null=True, blank=True) # 在使用Django设计数据库表时，
                            #如果设置null=True，则仅表示在数据库中该字段可以为空，但使用后台管理添加数据时仍然要需要输入值，因为Django自动做了数据验证不允许字段为空
                           #如果想要在Django中也可以将字段保存为空值，则需要添加另一个参数：blank=True
    mobile = models.CharField(u'手机', max_length=32)

    class Meta:
        verbose_name_plural = "用户表"

    def __str__(self):
        return self.name


class AdminInfo(models.Model):
    """
    用户登陆相关信息。公司有很多人，有人能登录我的系统，有人不能登录。
    """
    user_info = models.OneToOneField("UserProfile")

    username = models.CharField(u'用户名', max_length=64)
    password = models.CharField(u'密码', max_length=64)

    class Meta:
        verbose_name_plural = "管理员表"

    def __str__(self):
        return self.user_info.name


class UserGroup(models.Model):
    """
    用户组
    """
    name = models.CharField(max_length=32, unique=True)
    users = models.ManyToManyField('UserProfile')

    class Meta:
        verbose_name_plural = "用户组表"

    def __str__(self):
        return self.name


class BusinessUnit(models.Model):
    """
    业务线表（部门表）
    """
    name = models.CharField('业务线', max_length=64, unique=True)
    # 这里都是组，一个组里多个人
    contact = models.ForeignKey('UserGroup', verbose_name='业务联系人', related_name='c') # 多个人
    manager = models.ForeignKey('UserGroup', verbose_name='系统管理员', related_name='m') # 多个人

    class Meta:
        verbose_name_plural = "业务线表"

    def __str__(self):
        return self.name


class IDC(models.Model):
    """
    机房信息
    """
    name = models.CharField('机房', max_length=32)
    floor = models.IntegerField('楼层', default=1)

    class Meta:
        verbose_name_plural = "机房表"

    def __str__(self):
        return self.name


class Tag(models.Model):
    """
    资产标签
    """
    name = models.CharField('标签', max_length=32, unique=True)

    class Meta:
        verbose_name_plural = "标签表"

    def __str__(self):
        return self.name


class Asset(models.Model):
    """
    资产信息表，所有资产公共信息（服务器、交换机，服务器，防火墙等）
        一行资产记录要么对应一个网络设备，要么对应一台服务器
    """
    device_type_choices = ( #资产类型
        (1, '服务器'),
        (2, '交换机'),
        (3, '防火墙'),
    )
    device_status_choices = ( #资产状态
        (1, '上架'),
        (2, '在线'),
        (3, '离线'),
        (4, '下架'),
    )

    device_type_id = models.IntegerField(choices=device_type_choices, default=1)
    device_status_id = models.IntegerField(choices=device_status_choices, default=1)

    # 不管是网络设备还是服务器，都得放到一个机柜上
    cabinet_num = models.CharField('机柜号', max_length=30, null=True, blank=True)
    cabinet_order = models.CharField('机柜中序号', max_length=30, null=True, blank=True)

    # 机房，属于哪个机房
    idc = models.ForeignKey('IDC', verbose_name='IDC机房', null=True, blank=True)
    # 为什么把所属业务线放在Asset表中，因为你如果把这列放在服务器表和网络设备表，这两个表都得有这列，重复了。
    # 所以建立了Asset表，保存资产共有信息
    business_unit = models.ForeignKey('BusinessUnit', verbose_name='属于的业务线', null=True, blank=True)

    # 一篇文章可以给它打上标签。我们也可以给资产打个标签
    tag = models.ManyToManyField('Tag', blank=True)

    # 为什么要有最后修改时间？获取今天未采集资产时，怎么算为采集，就是根据这个最后修改时间
    latest_date = models.DateField(null=True)
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "资产表"

    def __str__(self):
        return "%s-%s-%s" % (self.idc.name, self.cabinet_num, self.cabinet_order)


class Server(models.Model):
    """
    服务器信息
    """
    asset = models.OneToOneField('Asset') #对应Asset表中的id列，Asset表保存的是资产共有属性，比如在哪个机房，在哪个机柜，属于哪个业务线
                                        ##等效于asset = models.Foreign('Asset', unique=True)

    hostname = models.CharField(max_length=128, unique=True)
    # 下面3个是主板的信息
    sn = models.CharField('SN号', max_length=64, db_index=True)
    manufacturer = models.CharField(verbose_name='制造商', max_length=64, null=True, blank=True)
    model = models.CharField('型号', max_length=64, null=True, blank=True)

    #每台服务器买完之后，出厂的时候会给一个管理ip，这个东西是干嘛的？你到我这买服务器，这个服务器还没装系统，但是在服务器
    #里面内置一个小的系统，通过这个管理ip就可以连上这台服务器，连上可以执行一些命令，让服务器重启或者干嘛干嘛的
    manage_ip = models.GenericIPAddressField('管理IP', null=True, blank=True)

    # 装的系统信息
    os_platform = models.CharField('系统', max_length=16, null=True, blank=True)
    os_version = models.CharField('系统版本', max_length=16, null=True, blank=True)

    #cpu信息
    cpu_count = models.IntegerField('CPU个数', null=True, blank=True)
    cpu_physical_count = models.IntegerField('CPU物理个数', null=True, blank=True)
    cpu_model = models.CharField('CPU型号', max_length=128, null=True, blank=True)

    create_at = models.DateTimeField(auto_now_add=True, blank=True)

    class Meta:
        verbose_name_plural = "服务器表"

    def __str__(self):
        return self.hostname


class NetworkDevice(models.Model):
    """
    网络设备表：除了服务器以外的设备，比如公司的路由器、交换机、防火墙设备
    """
    asset = models.OneToOneField('Asset')
    management_ip = models.CharField('管理IP', max_length=64, blank=True, null=True)
    vlan_ip = models.CharField('VlanIP', max_length=64, blank=True, null=True)
    intranet_ip = models.CharField('内网IP', max_length=128, blank=True, null=True)
    sn = models.CharField('SN号', max_length=64, unique=True)
    manufacture = models.CharField(verbose_name=u'制造商', max_length=128, null=True, blank=True)
    model = models.CharField('型号', max_length=128, null=True, blank=True)
    port_num = models.SmallIntegerField('端口个数', null=True, blank=True)
    device_detail = models.CharField('设置详细配置', max_length=255, null=True, blank=True)

    class Meta:
        verbose_name_plural = "网络设备"


class Disk(models.Model):
    """
    硬盘信息
    """
    slot = models.CharField('插槽位', max_length=8)
    model = models.CharField('磁盘型号', max_length=32)
    capacity = models.FloatField('磁盘容量GB')
    pd_type = models.CharField('磁盘类型', max_length=32)
    server_obj = models.ForeignKey('Server',related_name='disk')

    class Meta:
        verbose_name_plural = "硬盘表"

    def __str__(self):
        return self.slot


class NIC(models.Model):
    """
    网卡信息
    """
    name = models.CharField('网卡名称', max_length=128)
    hwaddr = models.CharField('网卡mac地址', max_length=64)
    netmask = models.CharField(max_length=64)
    ipaddrs = models.CharField('ip地址', max_length=256)
    up = models.BooleanField(default=False)
    server_obj = models.ForeignKey('Server',related_name='nic')


    class Meta:
        verbose_name_plural = "网卡表"

    def __str__(self):
        return self.name


class Memory(models.Model):
    """
    内存信息
    """
    slot = models.CharField('插槽位', max_length=32)
    manufacturer = models.CharField('制造商', max_length=32, null=True, blank=True)
    model = models.CharField('型号', max_length=64)
    capacity = models.FloatField('容量', null=True, blank=True)
    sn = models.CharField('内存SN号', max_length=64, null=True, blank=True)
    speed = models.CharField('速度', max_length=16, null=True, blank=True)

    server_obj = models.ForeignKey('Server',related_name='memory')


    class Meta:
        verbose_name_plural = "内存表"

    def __str__(self):
        return self.slot


class AssetRecord(models.Model):
    """
    资产变更记录,creator为空时，表示是资产汇报的数据。
    """
    asset_obj = models.ForeignKey('Asset', related_name='ar')
    content = models.TextField(null=True)
    creator = models.ForeignKey('UserProfile', null=True, blank=True)
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "资产记录表"

    def __str__(self):
        return "%s-%s-%s" % (self.asset_obj.idc.name, self.asset_obj.cabinet_num, self.asset_obj.cabinet_order)


class ErrorLog(models.Model):
    """
    错误日志,如：agent采集数据错误 或 运行错误
    """
    asset_obj = models.ForeignKey('Asset', null=True, blank=True)
    title = models.CharField(max_length=16)
    content = models.TextField()
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "错误日志表"

    def __str__(self):
        return self.title




# 环境组
class UrlGroup(models.Model):
    """
    定义导航项目的组
    """
    group_name = models.CharField('分类名称', max_length=100, unique=True)
    code = models.CharField('标签名称', max_length=100)
    createtime = models.DateTimeField(auto_now_add=True, null=True)
    updatetime = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        verbose_name = '导航分组'
        verbose_name_plural = '导航分组'

    def __str__(self):
        return self.group_name

# 组内环境具体信息
class UrlInfor(models.Model):
    """
    定义导航项目的具体信息
    """
    url_name = models.CharField('链接名称', max_length=100)
    url_path = models.CharField('链接', max_length=200)
    url_desc = models.TextField('链接描述', max_length=200)
    url_group = models.ForeignKey(to=UrlGroup, verbose_name='分类名称', related_name='group_set', to_field="id")
    createtime = models.DateTimeField(auto_now_add=True, null=True)
    updatetime = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        verbose_name = '导航详情'
        verbose_name_plural = '导航详情'
        ordering = ['url_name']

    def __str__(self):
        return self.url_name



