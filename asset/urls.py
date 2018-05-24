# -*- coding: utf-8 -*-

from django.conf.urls import url
from asset.views import account,home,views

urlpatterns = [
    url(r'^$', home.IndexView.as_view(), name='index'),

    url(r'^login.html$', account.login),
    url(r'^check_code.html$', account.check_code),
    url(r'^logout/', account.LogoutView.as_view()),

    url(r'^index.html$', home.IndexView.as_view()),

    url(r'^asset.html$', views.AssetView.as_view()),
    # url(r'^delete_host/', views.delete_host),
    url(r'^edit_host/', views.edit_host),

    url(r'^software/', views.software),
    url(r'^business/', views.business),
    url(r'^user.html$', views.user),

    url(r'^environment/', views.environment),

    url(r'^asset-(?P<device_type_id>\d+)-(?P<asset_nid>\d+).html$', views.AssetDetailView.as_view()),

]
