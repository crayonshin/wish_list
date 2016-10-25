from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^validate$', views.validate),
    url(r'^dashboard$', views.dashboard),
    url(r'^create$', views.create),
    url(r'^additem$', views.additem),
    url(r'^wishes/(?P<id>\d+)$', views.wishes),
    url(r'^logout$', views.logout),
    url(r'^deleteitem/(?P<id>\d+)$', views.deleteitem),
    url(r'^removeitem/(?P<id>\d+)$', views.removeitem),
    url(r'^addfromanother/(?P<id>\d+)$', views.addfromanother),
]
