from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.conf import settings
from django.contrib.auth import get_user_model

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

User = get_user_model()

class GoogleLoginAPIView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Login or register with Google",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['id_token'],
            properties={'id_token': openapi.Schema(type=openapi.TYPE_STRING)}
        ),
        responses={200: 'Tokens returned', 400: 'Invalid token'}
    )
    def post(self, request):
        token = request.data.get("id_token")
        if not token:
            return Response({"error": "id_token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            idinfo = id_token.verify_oauth2_token(
                token, google_requests.Request(), settings.GOOGLE_WEB_CLIENT_ID
            )

            email = idinfo["email"]
            name = idinfo.get("name", email.split("@")[0])
            picture = idinfo.get("picture")

            user, created = User.objects.get_or_create(email=email, defaults={"username": name})
            if created and picture:
                user.profile_picture = picture
                user.save()

            refresh = RefreshToken.for_user(user)

            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "username": user.username,
                    "email": user.email,
                    "role": getattr(user, 'role', 'user'),
                }
            })

        except ValueError:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import AllowAny
# from rest_framework import status
# from rest_framework_simplejwt.tokens import RefreshToken
# from django.conf import settings
# from django.contrib.auth import get_user_model
# from google.oauth2 import id_token
# from google.auth.transport import requests as google_requests

# User = get_user_model()

# class GoogleLoginAPIView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         token = request.data.get("id_token")
#         if not token:
#             return Response({"error": "id_token is required"}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             # Verify token for both Android and Web
#             idinfo = id_token.verify_oauth2_token(
#                 token, 
#                 google_requests.Request(),
#                 settings.GOOGLE_WEB_CLIENT_ID  # Use web client ID for both
#             )

#             # Additional check for Android tokens
#             if idinfo['aud'] not in [settings.GOOGLE_WEB_CLIENT_ID, settings.GOOGLE_ANDROID_CLIENT_ID]:
#                 raise ValueError("Invalid audience")

#             email = idinfo["email"]
#             name = idinfo.get("name", email.split("@")[0])
#             picture = idinfo.get("picture")

#             user, created = User.objects.get_or_create(
#                 email=email, 
#                 defaults={"username": name}
#             )
            
#             if created and picture:
#                 user.profile_picture = picture
#                 user.save()

#             refresh = RefreshToken.for_user(user)

#             return Response({
#                 "access": str(refresh.access_token),
#                 "refresh": str(refresh),
#                 "user": {
#                     "id": user.id,
#                     "username": user.username,
#                     "email": user.email,
#                     "role": user.role,
#                 }
#             })

#         except ValueError as e:
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)