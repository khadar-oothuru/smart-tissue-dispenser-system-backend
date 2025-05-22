from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.urls import reverse
from django.views import View
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..models import CustomUser

token_generator = PasswordResetTokenGenerator()

class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Send password reset link to email",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email'],
            properties={'email': openapi.Schema(type=openapi.TYPE_STRING, format='email')}
        ),
        responses={200: 'Email sent', 404: 'User not found'}
    )
    def post(self, request):
        email = request.data.get('email')
        try:
            user = CustomUser.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = token_generator.make_token(user)
            reset_url = f"{request.scheme}://{request.get_host()}{reverse('reset-password', args=[uid, token])}"

            html_message = render_to_string('emails/password_reset_email.html', {
                'user': user,
                'reset_url': reset_url,
            })

            send_mail(
                subject='🔒 Reset Your Password',
                message=f"Hi {user.username}, reset your password using the link below.",
                from_email='your_email@gmail.com',
                recipient_list=[email],
                html_message=html_message,
                fail_silently=False,
            )

            return Response({'message': 'Password reset link sent.'}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({'error': 'No account found with this email address.'}, status=status.HTTP_404_NOT_FOUND)


@method_decorator(csrf_protect, name='dispatch')
class ResetPasswordView(View):
    def get(self, request, uidb64, token):
        return render(request, 'reset_password_form.html', {'uidb64': uidb64, 'token': token})

    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)

            if not token_generator.check_token(user, token):
                return render(request, 'reset_password_form.html', {'error': 'Invalid or expired token.'})

            new_password = request.POST.get('password')
            if not new_password:
                return render(request, 'reset_password_form.html', {'error': 'Please enter a new password.'})

            user.set_password(new_password)
            user.save()
            return render(request, 'reset_password_form.html', {'message': 'Password reset successful.'})
        except Exception:
            return render(request, 'reset_password_form.html', {'error': 'Something went wrong. Try again.'})
