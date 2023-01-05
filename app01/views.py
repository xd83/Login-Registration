from django.contrib import messages
from django.http import HttpResponse, response
from django.shortcuts import render, redirect
from app01 import models
from .forms import UserForm
import json
# Create your views here.


def index(request):
  pass
  return render(request, 'index.html')


def login(request, message=""):
  if request.method == "POST":
    login_form = UserForm(request.POST)   # 数据验证
    message = "请检查填写的内容！"
    if login_form.is_valid():
      username = login_form.cleaned_data['username']
      password = login_form.cleaned_data['password']
      try:
        user = models.User.objects.get(name=username)
        if user.password == password:
          return redirect('/index/')
        else:
          message = "密码不正确！"
      except:
        message = "用户不存在！"
    return render(request, 'login.html', {'message':message, 'login_form':login_form})

  login_form = UserForm()
  return render(request, 'login.html', {'message':message, 'login_form':login_form})


def register(request):
  pass
  return render(request, 'register.html')


def logout(request):
  pass
  return redirect('/index/')
