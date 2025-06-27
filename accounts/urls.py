from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    path('register', views.RegisterUser.as_view(), name='registration'),
    path('verify-otp', views.VerifyOTP.as_view(), name='verify_otp'),
    path('login', views.LoginUser.as_view(), name='login'),
    path('complete-counsellor-profile/', views.CompleteCounsellorProfile.as_view(), name='complete-counsellor-profile'),

    path('update-counsellor-profile/<int:user_id>/', views.UpdateCounsellorProfile.as_view(), name='update-counsellor-profile'),


    path('users/', views.ListUsers.as_view(), name='list-users'),
    path('users/<int:user_id>/update/', views.UpdateUserView.as_view(), name='update-user'),
    path('users/<int:user_id>/toggle-active/', views.ToggleUserStatus.as_view(), name='toggle-user-status'),

    path('update-profile/', views.UpdateProfile.as_view(), name='update-profile'),

    path('create-user/',views.AdminByCreateUser.as_view(), name='admin-create-user'),

    path('send-reset-otp/', views.SendResetOTPView.as_view()),
    path('verify-reset-otp/', views.VerifyResetOTPView.as_view()),
    path('reset-password/', views.ResetPasswordView.as_view()),
]
# + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
