from django.contrib import messages
from django.http import HttpResponse, response
from django.shortcuts import render, redirect
from app01 import models
import json
# Create your views here.


def index(request):
  pass
  return render(request, 'index.html')


def login(request):
  pass
  return render(request, 'login.html')


def register(request):
  pass
  return render(request, 'register.html')


def logout(request):
  pass
  return redirect('/index/')
