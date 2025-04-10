from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('register', views.RegisterUser.as_view(), name='registration'),
    path('verify-otp', views.VerifyOTP.as_view(), name='verify_otp'),
    path('login', views.LoginUser.as_view(), name='login'),
    path('users/', views.ListUsers.as_view(), name='list-users'),
    path('users/<int:user_id>/update/', views.UpdateUserView.as_view(), name='update-user'),
    path('users/<int:user_id>/toggle-active/', views.ToggleUserStatus.as_view(), name='toggle-user-status'),

    path('update-profile/', views.UpdateProfile.as_view(), name='update-profile'),
]
