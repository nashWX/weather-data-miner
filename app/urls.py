from django.urls import path
from app import views

urlpatterns = [
    path('', views.authorize, name="authorize"),
    path('active-reports', views.activeReport, name="active-report"),
    path('warnings', views.warnings, name="warnings"),
]