from accounts.views import CustomUserRegisterView, CustomUserRegisterVerifyCodeView, LoginView , LoginVerify
from django.urls import path

app_name = "accounts"

urlpatterns = [
    path('register', CustomUserRegisterView.as_view(), name= 'user_register'),
    path('verify', CustomUserRegisterVerifyCodeView.as_view(), name = 'verify_code'),
    path('login', LoginView.as_view(), name = 'login'),
    path('verify-login', LoginVerify.as_view(), name = 'verify_login'),
]