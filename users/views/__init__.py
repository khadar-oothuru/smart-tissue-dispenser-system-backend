
# # users/views/__init__.py
# from .auth import (
#     RegisterView, 
#     CustomTokenObtainPairView,
#     UserDetailView,
#     UserUpdateView,
#     ChangePasswordView,
#     UploadProfilePictureView,
#     VerifyOTPView,
# )
# from .password_reset import ForgotPasswordView, ResetPasswordView
# from .google_auth import GoogleLoginAPIView
# from .admin_check import test_admin_permission

# __all__ = [
#     'RegisterView',
#     'CustomTokenObtainPairView',
#     'UserDetailView',
#     'UserUpdateView',
#     'ChangePasswordView',
#     'UploadProfilePictureView',
#     'VerifyOTPView',
#     'ForgotPasswordView',
#     'ResetPasswordView',
#     'GoogleLoginAPIView',
#     'test_admin_permission',
# ]

# # users/views/__init__.py
# from .auth import (
#     RegisterView, 
#     CustomTokenObtainPairView,
#     UserDetailView,
#     UserUpdateView,
#     ChangePasswordView,
#     UploadProfilePictureView,
#     VerifyOTPView,
#     SendChangePasswordOTPView,
#     VerifyPasswordChangeOTPView,
#     ChangePasswordWithOTPView,
# )
# from .password_reset import ForgotPasswordView, ResetPasswordView
# from .google_auth import GoogleLoginAPIView
# from .admin_check import test_admin_permission

# __all__ = [
#     'RegisterView',
#     'CustomTokenObtainPairView',
#     'UserDetailView',
#     'UserUpdateView',
#     'ChangePasswordView',
#     'UploadProfilePictureView',
#     'VerifyOTPView',
#     'SendChangePasswordOTPView',
#     'VerifyPasswordChangeOTPView',
#     'ChangePasswordWithOTPView',
#     'ForgotPasswordView',
#     'ResetPasswordView',
#     'GoogleLoginAPIView',
#     'test_admin_permission',
# ]


# users/views/__init__.py
from .auth import (
    RegisterView, 
    CustomTokenObtainPairView,
    UserDetailView,
    UserUpdateView,
    # ChangePasswordView,  # Remove this line
    UploadProfilePictureView,
    VerifyPasswordChangeOTPView,# Also remove this if it doesn't exist
    SendChangePasswordOTPView,
    VerifyPasswordChangeOTPView,
    ChangePasswordWithOTPView,
)
from .password_reset import ForgotPasswordView, ResetPasswordView  # Import VerifyOTPView from password_reset
from .google_auth import GoogleLoginAPIView
from .admin_check import test_admin_permission

__all__ = [
    'RegisterView',
    'CustomTokenObtainPairView',
    'UserDetailView',
    'UserUpdateView',
    # 'ChangePasswordView',  # Remove this
    'UploadProfilePictureView',
    # 'VerifyOTPView',
    'SendChangePasswordOTPView',
    'VerifyPasswordChangeOTPView',
    'ChangePasswordWithOTPView',
    'ForgotPasswordView',
    'ResetPasswordView',
    'GoogleLoginAPIView',
    'test_admin_permission',
]