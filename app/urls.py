from django.urls import path
from app import views

urlpatterns = [
    path('', views.authorize, name="authorize"),
    path('hashtags', views.hashtags, name="hashtags"),
    path('active-reports', views.activeReport, name="active-report"),
    path('about', views.about, name="about"),
    path('warning-update', views.warning_update, name="warning-update"),
    path('warning-list', views.warningList, name="warning-list"),
    path('download-media', views.download, name="download-media"),
]