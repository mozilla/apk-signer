from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^auth$', views.AuthView.as_view(), name='system.auth'),
    url(r'^cef$', views.CEFView.as_view(), name='system.cef'),
    url(r'^log$', views.LogView.as_view(), name='system.log'),
    url(r'^stats$', views.StatsView.as_view(), name='system.stats'),
    url(r'^trace$', views.TraceView.as_view(), name='system.trace'),
)
