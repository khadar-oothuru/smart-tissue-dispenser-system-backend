from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from users.views import (
    RegisterView,
    UserDetailView,
    CustomTokenObtainPairView,
    ForgotPasswordView,
    ResetPasswordView,
    test_admin_permission,
    GoogleLoginAPIView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('user/', UserDetailView.as_view(), name='user_detail'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('forgot/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset/<uidb64>/<token>/', ResetPasswordView.as_view(), name='reset-password'),
    path('google-login/', GoogleLoginAPIView.as_view(), name='google_login'),
    path('admin/test/', test_admin_permission, name='test_admin_permission'),
]
