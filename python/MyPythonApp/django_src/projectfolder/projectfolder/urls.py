# coding:utf-8
#http://blog1.erp2py.com/2010/10/djangojavascript.html

from django.conf.urls import patterns, include, url
from django.conf import settings # MEDIA_ROOTÇì«Ç›çûÇﬁÇΩÇﬂÇ…ïKóv

from django.contrib import admin
admin.autodiscover()

from projectfolder.pfol.views import *

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'projectfolder.views.home', name='home'),
    # url(r'^blog/', inclede('blog.urls')),
    url(r'^d3/$', d3_index),
    url(r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes':True}),
    url(r'^admin/', include(admin.site.urls)),
)
