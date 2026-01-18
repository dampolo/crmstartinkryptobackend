from django.urls import path
from . import views

urlpatterns = [
    path('me/', views.MeView.as_view(), name='me'),
    path('create-account/', views.RegistrationView.as_view(), name='create-account'),
    path('token/', views.CookieTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', views.CookieTokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', views.LogoutView.as_view(), name='logout')
]
