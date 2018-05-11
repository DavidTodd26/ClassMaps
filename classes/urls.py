from django.urls import path, re_path
from . import views
from .views import search
import django_cas_ng.views

app_name = 'classes'
urlpatterns = [
    re_path('^accounts/login$', django_cas_ng.views.login, name='cas_ng_login'),
    re_path('^accounts/logout$', django_cas_ng.views.logout, name='cas_ng_logout'),
    re_path('^accounts/callback$', django_cas_ng.views.callback, name='cas_ng_proxy_callback'),
    re_path('^$', views.index, name="index"),
    re_path('^remove/$', views.remove, name="remove"),
    re_path('^save/$', views.save, name="save"),
    re_path('^results/$', search, name="search"),
    re_path('^api/query/$', views.query, name='query'),
    re_path('^api/enroll/$', views.enroll, name='enroll'),
    re_path('^api/saved/$', views.saved_locations, name='saved_locations'),
    re_path('^course/(?P<id>.*)/$', views.course_details, name="course"),
    re_path('^building/(?P<id>.*)/$', views.building_details, name="building"),
    re_path('^about/$', views.about),
]
