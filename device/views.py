from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Device, DeviceData, Notification
from .serializers import DeviceSerializer, DeviceDataSerializer, NotificationSerializer

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

# ----------------------------
# Device Management
# ----------------------------

@swagger_auto_schema(
    method='post',
    request_body=DeviceSerializer,
    responses={201: DeviceSerializer, 400: 'Validation Error'},
    operation_description="Add a new device (Admin only)"
)
@api_view(['POST'])
@permission_classes([IsAdminUser])
def add_device(request):
    serializer = DeviceSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(added_by=request.user)
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@swagger_auto_schema(
    method='get',
    responses={200: DeviceSerializer(many=True)},
    operation_description="Get list of all devices (Authenticated users only)"
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_devices(request):
    devices = Device.objects.all()
    serializer = DeviceSerializer(devices, many=True)
    return Response(serializer.data)


@swagger_auto_schema(
    method='get',
    responses={200: DeviceSerializer(), 404: 'Device not found'},
    operation_description="Retrieve a device by ID"
)
@swagger_auto_schema(
    method='put',
    request_body=DeviceSerializer,
    responses={200: DeviceSerializer(), 400: 'Validation Error'},
    operation_description="Update a device by ID"
)
@swagger_auto_schema(
    method='delete',
    responses={200: 'Device deleted', 404: 'Device not found'},
    operation_description="Delete a device by ID"
)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def device_detail(request, pk):
    try:
        device = Device.objects.get(pk=pk)
    except Device.DoesNotExist:
        return Response({'error': 'Device not found'}, status=404)

    if request.method == 'GET':
        return Response(DeviceSerializer(device).data)
    elif request.method == 'PUT':
        serializer = DeviceSerializer(device, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    elif request.method == 'DELETE':
        device.delete()
        return Response({'message': 'Device deleted successfully'})


# ----------------------------
# Device Data Handling
# ----------------------------

device_data_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['DID', 'ALERT', 'count', 'REFER_Val', 'TAMPER'],
    properties={
        'DID': openapi.Schema(type=openapi.TYPE_INTEGER, description='Device ID'),
        'ALERT': openapi.Schema(type=openapi.TYPE_STRING, description='Alert status'),
        'count': openapi.Schema(type=openapi.TYPE_INTEGER, description='Usage count'),
        'REFER_Val': openapi.Schema(type=openapi.TYPE_INTEGER, description='Reference Value'),
        'TAMPER': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Tamper detection'),
    }
)

@swagger_auto_schema(
    method='post',
    request_body=device_data_schema,
    responses={201: 'Data recorded', 404: 'Device not found'},
    operation_description="Receive real-time data from devices (public access)"
)
@api_view(['POST'])
@permission_classes([AllowAny])
def receive_device_data(request):
    try:
        device = Device.objects.get(id=request.data.get('DID'))
        data = DeviceData.objects.create(
            device=device,
            alert=request.data.get('ALERT'),
            count=request.data.get('count'),
            refer_val=request.data.get('REFER_Val'),
            tamper=request.data.get('TAMPER')
        )

        if request.data.get('ALERT') == "LOW":
            Notification.objects.create(
                device=device,
                message=f"[{device.floor_number}-{device.room_number}] LOW tissue alert at {data.timestamp}"
            )
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "notifications",
                {
                    "type": "send_notification",
                    "content": {
                        "device_id": device.id,
                        "room": device.room_number,
                        "floor": device.floor_number,
                        "timestamp": str(data.timestamp),
                        "alert": "LOW tissue alert"
                    }
                }
            )
        return Response({"message": "Data recorded successfully"}, status=201)

    except Device.DoesNotExist:
        return Response({"error": "Device not found"}, status=404)


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


# ----------------------------
# Notifications & Analytics
# ----------------------------

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
    method='get',
    responses={200: 'List of device analytics'},
    operation_description="Get analytics like LOW alerts and last alert timestamp for each device"
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def device_analytics(request):
    devices = Device.objects.all()
    analytics = []

    for device in devices:
        low_alerts = DeviceData.objects.filter(device=device, alert="LOW").count()
        last_entry = DeviceData.objects.filter(device=device).order_by('-timestamp').first()
        analytics.append({
            "device_id": device.id,
            "room": device.room_number,
            "floor": device.floor_number,
            "low_alert_count": low_alerts,
            "last_alert_time": last_entry.timestamp if last_entry else None
        })

    return Response(analytics)
