from django.urls import path
from app import views

urlpatterns = [
    path('', views.authorize, name="authorize"),
    path('hashtags', views.hashtags, name="hashtags"),
    path('active-reports', views.activeReport, name="active-report"),
    # path('warnings', views.warnings, name="warnings"),
    path('warning-update', views.warning_update, name="warning-update"),
    path('warning-list', views.warningList, name="warning-list"),
]