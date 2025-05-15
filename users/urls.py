from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterView,
    UserDetailView,
    ForgotPasswordView,
    ResetPasswordView,
)

urlpatterns = [
    # User Registration and Detail
    path('register/', RegisterView.as_view(), name='register'),
    path('user/', UserDetailView.as_view(), name='user_detail'),

    # JWT Authentication
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Password Reset
    path('forgot/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset/<uidb64>/<token>/', ResetPasswordView.as_view(), name='reset-password'),
]
