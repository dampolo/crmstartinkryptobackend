from django.urls import path
from .views import CookieTokenObtainPairView, CookieTokenRefreshView, MeView, LogoutView

urlpatterns = [
    path('me/', MeView.as_view(), name='me'),
    path('token/', CookieTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout')
]
