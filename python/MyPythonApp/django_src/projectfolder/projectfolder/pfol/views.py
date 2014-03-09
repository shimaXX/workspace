# coding: utf-8

from django.shortcuts import render, render_to_response
from django.http import HttpResponse

def d3_index(request):
#    return HttpResponse('01_empty_page_template.html', mimetype='text/html')
    return render_to_response('01_empty_page_template.html',locals())