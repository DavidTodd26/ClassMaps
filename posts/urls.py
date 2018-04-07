from django.urls import path, re_path
from . import views
from .views import search


app_name = 'posts'
urlpatterns = [
    path('results/', search, name='search'),
    path('', views.index, name="index"),
    re_path(r'details/(?P<id>\d+)/', views.details, name="details"),
];