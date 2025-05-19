from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.urls import reverse
from django.views import View
from django.shortcuts import render
from google.oauth2 import id_token
# from google.auth.transport import requests as google_requests
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings

from .models import CustomUser
from .serializers import RegisterSerializer, UserSerializer, CustomTokenObtainPairSerializer

User = get_user_model()
token_generator = PasswordResetTokenGenerator()

# Registration
class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Register a new user",
        request_body=RegisterSerializer,
        responses={201: RegisterSerializer, 400: 'Validation Error'}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

# Get authenticated user details
class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get details of authenticated user",
        responses={200: UserSerializer()}
    )
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

# Custom JWT login with email
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    @swagger_auto_schema(
        operation_description="Login and get JWT token pair",
        request_body=CustomTokenObtainPairSerializer,
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token'),
                    'access': openapi.Schema(type=openapi.TYPE_STRING, description='Access token'),
                }
            ),
            400: 'Validation Error',
            401: 'Authentication Failed'
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

# Forgot Password View
class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Send password reset link to email",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email'],
            properties={'email': openapi.Schema(type=openapi.TYPE_STRING, format='email')}
        ),
        responses={
            200: openapi.Response('Password reset email sent'),
            404: 'Email not found'
        }
    )
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
                from_email='your_email@gmail.com',  # update with your sender email
                recipient_list=[email],
                html_message=html_message,
                fail_silently=False,
            )

            return Response({'message': 'Password reset link sent to your email.'}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({'error': 'No account found with this email address.'}, status=status.HTTP_404_NOT_FOUND)

# Reset Password View (HTML form rendering)
class ResetPasswordView(View):
    @swagger_auto_schema(
        operation_description="Render password reset form",
        manual_parameters=[
            openapi.Parameter('uidb64', openapi.IN_PATH, type=openapi.TYPE_STRING),
            openapi.Parameter('token', openapi.IN_PATH, type=openapi.TYPE_STRING)
        ],
        responses={200: 'Password reset form'}
    )
    def get(self, request, uidb64, token):
        return render(request, 'reset_password_form.html', {
            'uidb64': uidb64,
            'token': token,
        })

    @swagger_auto_schema(
        operation_description="Submit new password for reset",
        manual_parameters=[
            openapi.Parameter('uidb64', openapi.IN_PATH, type=openapi.TYPE_STRING),
            openapi.Parameter('token', openapi.IN_PATH, type=openapi.TYPE_STRING)
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['password'],
            properties={'password': openapi.Schema(type=openapi.TYPE_STRING, description='New password')}
        ),
        responses={
            200: 'Password reset success page',
            400: 'Error page'
        }
    )
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

# # Google OAuth Login View
# class GoogleLoginAPIView(APIView):
#     permission_classes = [AllowAny]

#     @swagger_auto_schema(
#         operation_description="Login or register user via Google OAuth2 id_token",
#         request_body=openapi.Schema(
#             type=openapi.TYPE_OBJECT,
#             required=['id_token'],
#             properties={
#                 'id_token': openapi.Schema(type=openapi.TYPE_STRING, description='Google OAuth2 ID token')
#             }
#         ),
#         responses={
#             200: openapi.Schema(
#                 type=openapi.TYPE_OBJECT,
#                 properties={
#                     'access': openapi.Schema(type=openapi.TYPE_STRING, description='Access token'),
#                     'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token'),
#                     'user': openapi.Schema(
#                         type=openapi.TYPE_OBJECT,
#                         properties={
#                             'username': openapi.Schema(type=openapi.TYPE_STRING),
#                             'email': openapi.Schema(type=openapi.TYPE_STRING, format='email'),
#                             'role': openapi.Schema(type=openapi.TYPE_STRING),
#                         }
#                     )
#                 }
#             ),
#             400: 'Invalid token or Bad Request'
#         }
#     )
#     def post(self, request):
#         token = request.data.get("id_token")
#         if not token:
#             return Response({"error": "id_token is required"}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             idinfo = id_token.verify_oauth2_token(
#                 token, google_requests.Request(), settings.GOOGLE_WEB_CLIENT_ID
#             )

#             email = idinfo["email"]
#             name = idinfo.get("name", email.split("@")[0])
#             picture = idinfo.get("picture")

#             user, created = User.objects.get_or_create(email=email, defaults={"username": name})
#             if created and picture:
#                 user.profile_picture = picture
#                 user.save()

#             refresh = RefreshToken.for_user(user)

#             return Response({
#                 "access": str(refresh.access_token),
#                 "refresh": str(refresh),
#                 "user": {
#                     "username": user.username,
#                     "email": user.email,
#                     "role": getattr(user, 'role', 'user'),  # fallback if role not set
#                 }
#             })

#         except ValueError:
#             return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
