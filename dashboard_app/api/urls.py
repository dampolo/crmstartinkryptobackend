from django.urls import path, include
from . import views


urlpatterns = [
    path('dashboard/', views.DashboardAPIView.as_view()),
]