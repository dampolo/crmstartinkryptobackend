from django.urls import path, include
from . import views
from . import views

urlpatterns = [
    path("accounts/", include("allauth.urls")),
    path("social/", include("dj_rest_auth.urls")),

    
    path('me/', views.MeView.as_view(), name='me'),
    path('create-account/', views.RegistrationView.as_view(), name='create-account'),
    path('token/', views.CookieTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', views.CookieTokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', views.ResetPasswordView.as_view(), name='reset-password'),
]
