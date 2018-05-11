#!/usr/bin/env python
# -*- coding:utf-8 -*-
from django.views import View
from django.shortcuts import render
from django.http import JsonResponse
from .account import auth
from django.utils.decorators import method_decorator

@method_decorator(auth, name='dispatch')
class IndexView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'index.html')


