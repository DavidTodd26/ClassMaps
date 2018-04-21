from django.urls import path, re_path
from . import views
from .views import search
import django_cas_ng.views

app_name = 'classes'
urlpatterns = [
    re_path('^accounts/login$', django_cas_ng.views.login, name='cas_ng_login'),
    re_path('^accounts/logout$', django_cas_ng.views.logout, name='cas_ng_logout'),
    re_path('^accounts/callback$', django_cas_ng.views.callback, name='cas_ng_proxy_callback'),
    #path('', views.login, name="login"),
    path('', views.index, name="index"),
    path('results/', search, name="search"),
    re_path('courses/(?P<id>.*)/', views.details, name="details"),
    re_path('buildings/(?P<id>.*)/', views.details, name="details"),
]
