from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from device.models import Device
from device.serializers import DeviceSerializer
# from Backend.device.permissions import IsCustomAdmin 
from device.permissions import IsCustomAdmin
 # Assuming this is a custom admin permission you have

# Add Device (Admin only)
@swagger_auto_schema(
    method='post',
    request_body=DeviceSerializer,
    responses={201: DeviceSerializer, 400: 'Validation Error'},
    operation_description="Add a new device (Admin only)"
)
@api_view(['POST'])
@permission_classes([IsCustomAdmin])
def add_device(request):
    serializer = DeviceSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(added_by=request.user)
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


# List all devices (Authenticated users)
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


# Device detail, update, delete
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

# Apply swagger decorators to device_detail separately if needed (optional)
