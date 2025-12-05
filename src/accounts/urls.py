from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from accounts.views import UserRegisterAPIView, UserProfileAPIView, UserUpdateAPIView

urlpatterns = [
    path("register/", UserRegisterAPIView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    path("me/", UserProfileAPIView.as_view(), name="user-profile"),
    path("me/update/", UserUpdateAPIView.as_view(), name="user-update"),
]
