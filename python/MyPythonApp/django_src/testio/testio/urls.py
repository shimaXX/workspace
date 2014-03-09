from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()
from testio.showtweet.vies import *

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'testio.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url("",include('django-socketio.urls')),
    url(r'^socket/$', system_message),
    url(r'^admin/', include(admin.site.urls)),
)
