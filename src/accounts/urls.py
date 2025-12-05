from django.urls import path
from .views import *
urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("me/update/", ProfileUpdateView.as_view(), name="profile_update"),
    path("users/", UserListView.as_view(), name="user_list")
]