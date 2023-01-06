import datetime
import hashlib

from django.contrib import messages
from django.http import HttpResponse, response
from django.shortcuts import render, redirect
from app01 import models, forms
from .forms import UserForm, RegisterForm
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
import json


# Create your views here.


def index(request):
  pass
  return render(request, 'index.html')


def login(request):
  if request.session.get('is_login', None):  # 不允许重复登录
    return redirect('/index/')
  if request.method == 'POST':
    login_form = forms.UserForm(request.POST)
    message = '请检查填写的内容！'
    if login_form.is_valid():
      username = login_form.cleaned_data.get('username')
      password = login_form.cleaned_data.get('password')

      try:
        user = models.User.objects.get(name=username)
      except:
        message = '用户不存在！'
        return render(request, 'login.html', locals())

      if not user.has_confirmed:
        message = '该用户还未经过邮件确认！'
        return render(request, 'login.html', locals())

      if user.password == hash_code(password):  # 哈希值和数据库内的值进行比对
        request.session['is_login'] = True
        request.session['user_id'] = user.id
        request.session['user_name'] = user.name
        return redirect('/index/')
      else:
        message = '密码不正确！'
        return render(request, 'login.html', locals())
    else:
      return render(request, 'login.html', locals())

  login_form = forms.UserForm()
  return render(request, 'login.html', locals())  # {'message':message, 'login_form':login_form}


def register(request):
  if request.session.get('is_login', None):
    # 登录状态不允许注册。你可以修改这条原则！
    return redirect("/index/")
  if request.method == "POST":
    register_form = RegisterForm(request.POST)
    message = "请检查填写的内容！"
    if register_form.is_valid():  # 获取数据
      username = register_form.cleaned_data['username']
      password1 = register_form.cleaned_data['password1']
      password2 = register_form.cleaned_data['password2']
      email = register_form.cleaned_data['email']
      sex = register_form.cleaned_data['sex']
      if password1 != password2:  # 判断两次密码是否相同
        message = "两次输入的密码不同！"
        return render(request, 'register.html', locals())
      else:
        same_name_user = models.User.objects.filter(name=username)
        if same_name_user:  # 用户名唯一
          message = '用户已经存在，请重新选择用户名！'
          return render(request, 'register.html', locals())
        same_email_user = models.User.objects.filter(email=email)
        if same_email_user:  # 邮箱地址唯一
          message = '该邮箱地址已被注册，请使用别的邮箱！'
          return render(request, 'register.html', locals())

        # 当一切都OK的情况下，创建新用户

        new_user = models.User.objects.create()
        new_user.name = username
        new_user.password = hash_code(password1)
        new_user.email = email
        new_user.sex = sex
        new_user.save()

        code = make_confirm_string(new_user)
        send_email(email, code)

        message = '请前往邮箱进行确认！'
        return render(request, 'confirm.html', locals())
    else:
      return render(request, 'register.html', locals())
  register_form = RegisterForm()
  return render(request, 'register.html', locals())


def logout(request):
  if not request.session.get('is_login', None):
    # 如果本来就未登录，也就没有登出一说
    return redirect("/login/")
  request.session.flush()
  # 或者使用下面的方法
  # del request.session['is_login']
  return redirect("/login/")


def hash_code(s, salt='mysite'):  # 加点盐
  h = hashlib.sha256()
  s += salt
  h.update(s.encode('utf-8'))  # update方法只接收bytes类型
  return h.hexdigest()


def make_confirm_string(user):
  now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  code = hash_code(user.name, now)
  models.ConfirmString.objects.create(code=code, user=user, )
  return code


def send_email(email, code):

  subject = '来自测试的注册确认邮件'

  text_content = '''感谢注册,灵活使用搜索引擎www.baidu.com，可以更好学习Python、Django知识！\
                    如果你看到这条消息，说明你的邮箱服务器不提供HTML链接功能，请联系管理员！'''

  html_content = '''
                    <p>感谢注册<a href="http://{}/confirm/?code={}" target=blank>www.baidu.com</a>，\
                    活用搜索引擎更好学习Python、Django知识！</p>
                    <p>请点击站点链接完成注册确认！</p>
                    <p>此链接有效期为{}天！</p>
                    '''.format('127.0.0.1:8000', code, settings.CONFIRM_DAYS)

  msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
  msg.attach_alternative(html_content, "text/html")
  msg.send()


def user_confirm(request):
  code = request.GET.get('code', None)
  message = ''
  try:
    confirm = models.ConfirmString.objects.get(code=code)
  except:
    message = '无效的确认请求!'
    return render(request, 'confirm.html', locals())

  c_time = confirm.c_time
  now = datetime.datetime.now()
  if now > c_time + datetime.timedelta(settings.CONFIRM_DAYS):
    confirm.user.delete()
    message = '您的邮件已经过期！请重新注册!'
    return render(request, 'confirm.html', locals())
  else:
    confirm.user.has_confirmed = True
    confirm.user.save()
    confirm.delete()
    message = '确认成功，请使用账户登录！'
    return render(request, 'confirm.html', locals())
