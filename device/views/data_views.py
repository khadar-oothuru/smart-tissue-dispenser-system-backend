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

            tokens = ExpoPushToken.objects.all()
            for token_entry in tokens:
                send_push_notification(
                    token_entry.token,
                    title="🚨 LOW Tissue Alert",
                    body=f"Device {device.room_number} (Floor {device.floor_number}) triggered a LOW alert",
                    data={"device_id": device.id}
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
