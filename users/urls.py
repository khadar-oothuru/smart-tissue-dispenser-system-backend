from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    UserDetailView,
    ForgotPasswordView,
    ResetPasswordView,
    GoogleLoginView,
    CustomTokenObtainPairView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('user/', UserDetailView.as_view(), name='user_detail'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('forgot/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset/<uidb64>/<token>/', ResetPasswordView.as_view(), name='reset-password'),
    path('google-login/', GoogleLoginView.as_view(), name='google-login'),
]
