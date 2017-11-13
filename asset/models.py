from django.db import models

# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=64, null=False, unique=True)
    password = models.CharField(max_length=60, null=False)
    email = models.CharField(max_length=60)
    createtime = models.DateTimeField(auto_now_add=True, null=True)
    updatetime = models.DateTimeField(auto_now=True, null=True)


# 主机
class Host(models.Model):
    ip = models.GenericIPAddressField(protocol="ipv4", db_index=True)
    hostname = models.CharField(max_length=60, null=False)
    createtime = models.DateTimeField(auto_now_add=True, null=True)
    updatetime = models.DateTimeField(auto_now=True, null=True) #更新时间 列，但是要想让django去更新这个字段，有条件：
        # obj = UserGroup.objects.filter(id=1).update(caption='CEO') #这种更新，django不会去更新uptime列，必须使用下面3句话方式去更新，才会生效uptime列。
        # obj = UserGroup.objects.filter(id=1).first()
        # obj.caption = "CEO"
        # obj.save()
    b = models.ForeignKey(to="Business", to_field="id")
    e = models.ForeignKey(to="EngineRoom", to_field="id")

# 业务线
class Business(models.Model):
    caption = models.CharField(max_length=32, null=False, unique=True)
    code = models.CharField(max_length=32, null=False, default="SA") #业务线英文简称
    createtime = models.DateTimeField(auto_now_add=True, null=True)
    updatetime = models.DateTimeField(auto_now=True, null=True)

# 机房
class EngineRoom(models.Model):
    name = models.CharField(max_length=64, null=False, unique=True)
    createtime = models.DateTimeField(auto_now_add=True, null=True)
    updatetime = models.DateTimeField(auto_now=True, null=True)

# 软件
class Software(models.Model):
    name = models.CharField(max_length=32, null=False)
    createtime = models.DateTimeField(auto_now_add=True, null=True)
    updatetime = models.DateTimeField(auto_now=True, null=True)
    r = models.ManyToManyField("Host")
