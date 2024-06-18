from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload_video, name='upload_video'),
    path('success/', views.upload_success, name='upload_success'),
    path('search/', views.search_videos, name='search_videos'),
    path('error/', views.error, name='error'),
]
