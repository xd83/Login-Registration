from django.contrib import messages
from django.http import HttpResponse, response
from django.shortcuts import render, redirect
from app01 import models
import json
# Create your views here.
def home(requests):

  return render(requests, 'login.html')
