from .auth import RegisterView, CustomTokenObtainPairView
from .password_reset import ForgotPasswordView, ResetPasswordView
from .auth import UserDetailView
from .admin_check import test_admin_permission
from .google_auth import GoogleLoginAPIView

__all__ = [
    "RegisterView",
    "CustomTokenObtainPairView",
    "ForgotPasswordView",
    "ResetPasswordView",
    "UserDetailView",
    "GoogleLoginAPIView",
    "test_admin_permission",
]
