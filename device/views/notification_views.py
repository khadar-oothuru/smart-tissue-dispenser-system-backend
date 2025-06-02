
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.shortcuts import get_object_or_404

from device.models import Notification, ExpoPushToken, Device
from device.serializers import NotificationSerializer

@swagger_auto_schema(
    method='get',
    responses={200: NotificationSerializer(many=True)},
    operation_description="Fetch all notifications for the authenticated user"
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_notifications(request):
    # Check if the user is an admin
    if hasattr(request.user, 'role') and request.user.role == 'admin':
        # Admin can see all notifications
        notifications = Notification.objects.all().order_by('-created_at')
    else:
        # Regular users see only notifications for devices they added
        user_devices = Device.objects.filter(added_by=request.user)
        notifications = Notification.objects.filter(
            device__in=user_devices
        ).order_by('-created_at')
    
    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data)

@swagger_auto_schema(
    method='delete',
    responses={204: 'Notification deleted successfully'},
    operation_description="Delete a specific notification"
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_notification(request, pk):
    try:
        if hasattr(request.user, 'role') and request.user.role == 'admin':
            # Admin can delete any notification
            notification = Notification.objects.get(pk=pk)
        else:
            # Regular users can only delete notifications for their devices
            user_devices = Device.objects.filter(added_by=request.user)
            notification = Notification.objects.get(
                pk=pk,
                device__in=user_devices
            )
        
        notification.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Notification.DoesNotExist:
        return Response(
            {'error': 'Notification not found or you do not have permission to delete it'},
            status=status.HTTP_404_NOT_FOUND
        )

@swagger_auto_schema(
    method='post',
    responses={200: 'Notification marked as read'},
    operation_description="Mark a notification as read"
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notification_as_read(request, pk):
    try:
        if hasattr(request.user, 'role') and request.user.role == 'admin':
            notification = Notification.objects.get(pk=pk)
        else:
            user_devices = Device.objects.filter(added_by=request.user)
            notification = Notification.objects.get(
                pk=pk,
                device__in=user_devices
            )
        
        notification.is_read = True
        notification.save()
        serializer = NotificationSerializer(notification)
        return Response(serializer.data)
    except Notification.DoesNotExist:
        return Response(
            {'error': 'Notification not found'},
            status=status.HTTP_404_NOT_FOUND
        )

@swagger_auto_schema(
    method='post',
    responses={200: 'All notifications cleared'},
    operation_description="Clear all notifications for the authenticated user"
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clear_all_notifications(request):
    if hasattr(request.user, 'role') and request.user.role == 'admin':
        # Admin can clear all notifications
        deleted_count = Notification.objects.all().delete()[0]
    else:
        # Regular users can only clear notifications for their devices
        user_devices = Device.objects.filter(added_by=request.user)
        deleted_count = Notification.objects.filter(
            device__in=user_devices
        ).delete()[0]
    
    return Response({
        'message': f'{deleted_count} notifications cleared successfully'
    })

@swagger_auto_schema(
    method='get',
    responses={200: openapi.Response('Unread count', schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'count': openapi.Schema(type=openapi.TYPE_INTEGER)
        }
    ))},
    operation_description="Get unread notification count"
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_unread_count(request):
    if hasattr(request.user, 'role') and request.user.role == 'admin':
        count = Notification.objects.filter(is_read=False).count()
    else:
        user_devices = Device.objects.filter(added_by=request.user)
        count = Notification.objects.filter(
            device__in=user_devices,
            is_read=False
        ).count()
    
    return Response({'count': count})

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
        return Response({'error': 'Token is required'}, status=status.HTTP_400_BAD_REQUEST)

    ExpoPushToken.objects.update_or_create(
        user=request.user, 
        defaults={'token': token}
    )
    return Response({'message': 'Push token registered successfully'})