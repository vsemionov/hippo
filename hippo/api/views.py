from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse

from . import tasks


def index(request):
    return HttpResponse(str(tasks.add.delay(2, 2).get()))
    #return HttpResponse("aaa")
