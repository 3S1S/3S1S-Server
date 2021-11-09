from django.conf.urls import url
from django.contrib import admin
from django.urls import path
from testapp import views
from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")