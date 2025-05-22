from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from device.models import Notification, ExpoPushToken
from device.serializers import NotificationSerializer

@swagger_auto_schema(
    method='get',
    responses={200: NotificationSerializer(many=True)},
    operation_description="Fetch all system notifications (sorted by recent)"
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_notifications(request):
    notifications = Notification.objects.all().order_by('-created_at')
    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data)


@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['token'],
        properties={
            'token': openapi.Schema(type=openapi.TYPE_STRING, description='Expo push token')
        }
    ),
    responses={200: openapi.Response('Push token registered')},
    operation_description="Register Expo push token for authenticated user"
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_push_token(request):
    token = request.data.get('token')
    if not token:
        return Response({'error': 'Token is required'}, status=400)

    ExpoPushToken.objects.update_or_create(user=request.user, defaults={'token': token})
    return Response({'message': 'Push token registered successfully'})
