from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from device.models import Device, DeviceData, Notification, ExpoPushToken
from device.serializers import DeviceDataSerializer
from device.utils import send_push_notification

device_data_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['DID', 'ALERT', 'count', 'REFER_Val', 'TAMPER'],
    properties={
        'DID': openapi.Schema(type=openapi.TYPE_INTEGER),
        'ALERT': openapi.Schema(type=openapi.TYPE_STRING),
        'count': openapi.Schema(type=openapi.TYPE_INTEGER),
        'REFER_Val': openapi.Schema(type=openapi.TYPE_INTEGER),
        'TAMPER': openapi.Schema(type=openapi.TYPE_BOOLEAN),
    }
)

@swagger_auto_schema(
    method='post',
    request_body=device_data_schema,
    responses={201: openapi.Response('Success'), 404: 'Device not found'},
    operation_description="Receive real-time data from devices (public)"
)
@api_view(['POST'])
@permission_classes([AllowAny])
def receive_device_data(request):
    try:
        device = Device.objects.get(id=request.data.get('DID'))
        
       
        tamper_value = str(request.data.get('TAMPER')).lower()
        
        data = DeviceData.objects.create(
            device=device,
            alert=request.data.get('ALERT'),
            count=request.data.get('count'),
            refer_val=request.data.get('REFER_Val'),
            tamper=tamper_value
        )

        # Check conditions for notifications
        alert_status = request.data.get('ALERT')
        is_low_alert = alert_status == "LOW"
        is_tampered = tamper_value == "true"
        
        notifications_to_send = []
        
        # Check all three conditions
        if is_low_alert and is_tampered:
            # Both conditions are true - CRITICAL
            notifications_to_send.append({
                "type": "critical",
                "title": "🚨 CRITICAL Alert",
                "message": f"[Room {device.room_number}, Floor {device.floor_number}] Low tissue AND tampering detected!"
            })
        elif is_low_alert:
            # Only LOW alert
            notifications_to_send.append({
                "type": "low",
                "title": "⚠️ Low Tissue Alert",
                "message": f"[Room {device.room_number}, Floor {device.floor_number}] Low tissue detected"
            })
        elif is_tampered:
            # Only TAMPER alert
            notifications_to_send.append({
                "type": "tamper",
                "title": "🔒 Tamper Alert",
                "message": f"[Room {device.room_number}, Floor {device.floor_number}] Device tampering detected"
            })
        
        # Send all applicable notifications
        for notif_data in notifications_to_send:
            # Create notification record
            notification = Notification.objects.create(
                device=device,
                message=notif_data["message"]
            )
            
            
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "notifications",
                {
                    "type": "send_notification",
                    "content": {
                        "id": notification.id,
                        "device_id": device.id,
                        "room": device.room_number,
                        "floor": device.floor_number,
                        "timestamp": str(data.timestamp),
                        "alert": alert_status,
                        "tamper": tamper_value,
                        "notification_type": notif_data["type"],
                        "title": notif_data["title"],
                        "message": notif_data["message"],
                        "created_at": str(notification.created_at)
                    }
                }
            )
            
            
            tokens = ExpoPushToken.objects.all()
            for token_entry in tokens:
                try:
                    send_push_notification(
                        token_entry.token,
                        title=notif_data["title"],
                        body=notif_data["message"],
                        data={
                            "device_id": device.id,
                            "notification_id": notification.id,
                            "type": notif_data["type"]
                        }
                    )
                except Exception as e:
                    print(f"Failed to send push notification to {token_entry.token}: {e}")

        return Response({
            "message": "Data recorded successfully",
            "notifications_sent": len(notifications_to_send),
            "notification_types": [n["type"] for n in notifications_to_send]
        }, status=201)

    except Device.DoesNotExist:
        return Response({"error": "Device not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@swagger_auto_schema(
    method='get',
    responses={200: DeviceDataSerializer(many=True)},
    operation_description="Get all recorded device data"
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_device_data(request):
    data = DeviceData.objects.all()
    serializer = DeviceDataSerializer(data, many=True)
    return Response(serializer.data)


@swagger_auto_schema(
    method='get',
    responses={200: DeviceDataSerializer(many=True)},
    operation_description="Get device data by specific device ID"
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def device_data_by_id(request, device_id):
    data = DeviceData.objects.filter(device__id=device_id)
    serializer = DeviceDataSerializer(data, many=True)
    return Response(serializer.data)
