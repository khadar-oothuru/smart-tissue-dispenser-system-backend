
# from django.urls import path
# from rest_framework_simplejwt.views import TokenRefreshView

# from users.views import (
#     RegisterView,
#     UserDetailView,
#     UserUpdateView,  # Add this
#     CustomTokenObtainPairView,
#     ForgotPasswordView,
#     VerifyOTPView,  # Add this
#     ResetPasswordView,
#     ChangePasswordView,  # Add this
#     UploadProfilePictureView,  # Add this
#     test_admin_permission,
#     GoogleLoginAPIView,
# )

# urlpatterns = [
#     path('register/', RegisterView.as_view(), name='register'),
#     path('user/', UserDetailView.as_view(), name='user_detail'),
#     path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
#     path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
#     # Updated/New user profile endpoints
#     path('user/update/', UserUpdateView.as_view(), name='user_update'),
#     path('user/upload-picture/', UploadProfilePictureView.as_view(), name='upload_picture'),
#     path('user/change-password/', ChangePasswordView.as_view(), name='change_password'),
    
#     # Updated password reset endpoints with OTP
#     path('forgot/', ForgotPasswordView.as_view(), name='forgot_password'),  # Keep existing
#     path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),  # New
#     path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),  # New OTP-based reset
#     path('reset/<uidb64>/<token>/', ResetPasswordView.as_view(), name='reset-password'),  # Keep existing token-based
    
#     # Existing endpoints
#     path('google-login/', GoogleLoginAPIView.as_view(), name='google_login'),
#     path('admin/test/', test_admin_permission, name='test_admin_permission'),
# ]



from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from users.views import (
    RegisterView,
    UserDetailView,
    UserUpdateView,
    CustomTokenObtainPairView,
    ForgotPasswordView,
    VerifyPasswordChangeOTPView,
    ResetPasswordView,
    # ChangePasswordView,  # Remove this
    UploadProfilePictureView,
    SendChangePasswordOTPView,
    VerifyPasswordChangeOTPView,
    ChangePasswordWithOTPView,
    test_admin_permission,
    GoogleLoginAPIView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('user/', UserDetailView.as_view(), name='user_detail'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User profile endpoints
    path('user/update/', UserUpdateView.as_view(), name='user_update'),
    path('user/upload-picture/', UploadProfilePictureView.as_view(), name='upload_picture'),
    # path('user/change-password/', ChangePasswordView.as_view(), name='change_password'),  # Remove or comment out
    
    # Password change with OTP endpoints
    path('user/send-change-password-otp/', SendChangePasswordOTPView.as_view(), name='send_change_password_otp'),
    path('user/verify-password-change-otp/', VerifyPasswordChangeOTPView.as_view(), name='verify_password_change_otp'),
    path('user/change-password-with-otp/', ChangePasswordWithOTPView.as_view(), name='change_password_with_otp'),
    
    # Password reset endpoints with OTP
    path('forgot/', ForgotPasswordView.as_view(), name='forgot_password'),
    # path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    # path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    # path('reset/<uidb64>/<token>/', ResetPasswordView.as_view(), name='reset-password-legacy'),
    path('forgot/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset/<uidb64>/<token>/', ResetPasswordView.as_view(), name='reset-password'),
    
    # Other endpoints
    path('google-login/', GoogleLoginAPIView.as_view(), name='google_login'),
    path('admin/test/', test_admin_permission, name='test_admin_permission'),
]