from django.urls import path
from .views import CookieTokenObtainPairView, CookieTokenRefreshView, me

urlpatterns = [
    path('me/', me),
    path('token/', CookieTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
]
