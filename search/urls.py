__author__ = 'amywieliczka, jblowe'

from django.conf.urls import patterns, url
from search import views

urlpatterns = patterns('',
                       url(r'^search/$', views.search, name='search'),
                       url(r'^results/$', views.retrieveResults, name='retrieveResults'),
                       url(r'^bmapper/$', views.bmapper, name='bmapper'),
                       url(r'^csv/$', views.csv, name='csv'),
                       url(r'^gmapper/$', views.gmapper, name='gmapper'),
                       )