from django.conf.urls.defaults import patterns, include, url
from votes.views import votefeeling, login, home, index
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^votehome/$', votefeeling),
    url(r'^login$', login),
    url(r'^$', index),
    url(r'^home$', votefeeling),
    # Examples:
    # url(r'^$', 'VoteFeering.views.home', name='home'),
    # url(r'^VoteFeering/', include('VoteFeering.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    #url(r'^admin/', include('admin.site.urls')),
)
