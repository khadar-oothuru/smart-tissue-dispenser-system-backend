from rest_framework import generics, exceptions, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.urls import reverse

from .models import CustomUser
from .serializers import (
    RegisterSerializer,
    UserSerializer,  # Ensure this exists
)

User = get_user_model()
token_generator = PasswordResetTokenGenerator()

# ------------------ User Registration ------------------
class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

# ------------------ Get Authenticated User Info ------------------
class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

# ------------------ JWT Login with Email ------------------
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role  # Add custom claim
        return token

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if not email or not password:
            raise exceptions.AuthenticationFailed("Both email and password are required.")

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise exceptions.AuthenticationFailed("User with this email does not exist.")

        if not user.check_password(password):
            raise exceptions.AuthenticationFailed("Incorrect password.")

        refresh = self.get_token(user)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

# ------------------ Forgot Password ------------------
class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = token_generator.make_token(user)
            reset_path = reverse('reset-password', args=[uid, token])
            reset_url = f"{request.scheme}://{request.get_host()}{reset_path}"

            send_mail(
                subject='Password Reset Request',
                message=f"Hi {user.username},\n\nClick the link below to reset your password:\n{reset_url}",
                from_email='your_email@gmail.com',
                recipient_list=[email],
                fail_silently=False,
            )

            return Response({'message': 'Password reset link sent to your email.'}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({'error': 'No account found with this email address.'}, status=status.HTTP_404_NOT_FOUND)

# # ------------------ Reset Password ------------------
# class ResetPasswordView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request, uidb64, token):
#         try:
#             uid = force_str(urlsafe_base64_decode(uidb64))
#             user = User.objects.get(pk=uid)

#             if not token_generator.check_token(user, token):
#                 return Response({'error': 'Invalid or expired password reset token.'}, status=status.HTTP_400_BAD_REQUEST)

#             new_password = request.data.get('password')
#             if not new_password:
#                 return Response({'error': 'New password is required.'}, status=status.HTTP_400_BAD_REQUEST)

#             user.set_password(new_password)
#             user.save()

#             return Response({'message': 'Password has been reset successfully.'}, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response({'error': 'Something went wrong. Please try again.'}, status=status.HTTP_400_BAD_REQUEST)


from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages

class ResetPasswordView(View):
    def get(self, request, uidb64, token):
        return render(request, 'reset_password_form.html', {
            'uidb64': uidb64,
            'token': token,
        })

    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)

            if not token_generator.check_token(user, token):
                return render(request, 'reset_password_form.html', {
                    'error': 'Invalid or expired token.',
                })

            new_password = request.POST.get('password')
            if not new_password:
                return render(request, 'reset_password_form.html', {
                    'error': 'Please enter a new password.',
                })

            user.set_password(new_password)
            user.save()
            return render(request, 'reset_password_form.html', {
                'message': 'Password has been reset successfully.',
            })

        except Exception as e:
            return render(request, 'reset_password_form.html', {
                'error': 'Something went wrong. Please try again.',
            })
