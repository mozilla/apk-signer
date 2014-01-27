from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^$', views.SignView.as_view(), name='sign'),
)
