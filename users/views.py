from rest_framework import generics, exceptions, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.urls import reverse
from django.views import View
from django.shortcuts import render

from .models import CustomUser
from .serializers import RegisterSerializer, UserSerializer

User = get_user_model()
token_generator = PasswordResetTokenGenerator()

# Registration
class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

# Get authenticated user details
class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

# Custom JWT login with email
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
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

# Forgot Password View
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

            html_message = render_to_string('emails/password_reset_email.html', {
                'user': user,
                'reset_url': reset_url,
            })

            send_mail(
                subject='🔒 Reset Your Password',
                message=f"Hi {user.username}, use the link below to reset your password.",
                from_email='your_email@gmail.com',
                recipient_list=[email],
                html_message=html_message,
                fail_silently=False,
            )

            return Response({'message': 'Password reset link sent to your email.'}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({'error': 'No account found with this email address.'}, status=status.HTTP_404_NOT_FOUND)

# Reset Password View (HTML form rendering)
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
                return render(request, 'reset_password_form.html', {'error': 'Invalid or expired token.'})

            new_password = request.POST.get('password')
            if not new_password:
                return render(request, 'reset_password_form.html', {'error': 'Please enter a new password.'})

            user.set_password(new_password)
            user.save()
            return render(request, 'reset_password_form.html', {'message': 'Password has been reset successfully.'})

        except Exception:
            return render(request, 'reset_password_form.html', {'error': 'Something went wrong. Please try again.'})

# Google OAuth Login View


# from google.oauth2 import id_token
# from google.auth.transport import requests
# from rest_framework_simplejwt.tokens import RefreshToken
# from rest_framework.permissions import AllowAny
# from rest_framework.views import APIView

# class GoogleLoginView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         token = request.data.get('id_token')
#         if not token:
#             return Response({"error": "No id_token provided."}, status=400)

#         try:
#             idinfo = id_token.verify_oauth2_token(token, requests.Request(), 'YOUR_GOOGLE_CLIENT_ID')

#             email = idinfo['email']
#             username = idinfo.get('name', email.split('@')[0])
#             picture = idinfo.get('picture')

#             user, created = User.objects.get_or_create(email=email, defaults={
#                 'username': username,
#                 'role': 'user',
#                 'profile_picture': picture or None,
#             })

#             if not user.username:
#                 user.username = username
#             if picture and user.profile_picture != picture:
#                 user.profile_picture = picture
#             user.save()

#             refresh = RefreshToken.for_user(user)

#             return Response({
#                 'refresh': str(refresh),
#                 'access': str(refresh.access_token),
#                 'user': {
#                     'id': user.id,
#                     'email': user.email,
#                     'username': user.username,
#                     'role': user.role,
#                     'profile_picture': user.profile_picture,
#                 }
#             })

#         except ValueError:
#             return Response({"error": "Invalid token"}, status=400)


# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from google.oauth2 import id_token
# from google.auth.transport import requests
# from django.contrib.auth import get_user_model
# from rest_framework_simplejwt.tokens import RefreshToken
# from django.conf import settings

# User = get_user_model()

# class GoogleLoginAPIView(APIView):
#     def post(self, request):
#         token = request.data.get("id_token")
#         if not token:
#             return Response({"error": "Token is required"}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             # Verify token using Google
#             idinfo = id_token.verify_oauth2_token(
#                 token, requests.Request(), settings.GOOGLE_WEB_CLIENT_ID
#             )

#             # Extract user info
#             email = idinfo["email"]
#             name = idinfo.get("name", email.split("@")[0])
#             picture = idinfo.get("picture")

#             # Get or create user
#             user, created = User.objects.get_or_create(email=email, defaults={"username": name})
#             if created and picture:
#                 user.profile_picture = picture
#                 user.save()

#             # Generate JWT tokens
#             refresh = RefreshToken.for_user(user)

#             return Response({
#                 "access": str(refresh.access_token),
#                 "refresh": str(refresh),
#                 "user": {
#                     "username": user.username,
#                     "email": user.email,
#                     "role": user.role,
#                 }
#             })

#         except ValueError:
#             return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


# from rest_framework.views import APIView
# from rest_framework.response import Response

# class GoogleLoginView(APIView):
#     def post(self, request):
#         return Response({'message': 'Google login successful'})
