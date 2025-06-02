

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging

from device.models import Device
from device.serializers import DeviceSerializer
from device.permissions import IsCustomAdmin

logger = logging.getLogger(__name__)


# ✅ Add Device (Admin Only) - Updated to support registration_type
@swagger_auto_schema(
    method='post',
    request_body=DeviceSerializer,
    responses={201: DeviceSerializer, 400: 'Validation Error'},
    operation_description="Add a new device manually. Only accessible to admin users."
)
@api_view(['POST'])
@permission_classes([IsCustomAdmin])
def add_device(request):
    serializer = DeviceSerializer(data=request.data)
    if serializer.is_valid():
        # Manual registration with registration_type if your model has it
        save_kwargs = {'added_by': request.user}
        
        # Only add registration_type if the field exists in your model
        if hasattr(Device, 'registration_type'):
            save_kwargs['registration_type'] = 'manual'
        
        serializer.save(**save_kwargs)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ✅ List All Devices (Authenticated Users) - No changes needed
@swagger_auto_schema(
    method='get',
    responses={200: DeviceSerializer(many=True)},
    operation_description="Retrieve a list of all registered devices. Requires authentication."
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_devices(request):
    paginator = PageNumberPagination()
    paginator.page_size = 20

    # Select all fields including metadata if it exists
    fields_to_select = ['id', 'name', 'floor_number', 'room_number', 'device_id', 'created_at', 'added_by']
    
    # Add optional fields if they exist in your model
    if hasattr(Device, 'metadata'):
        fields_to_select.append('metadata')
    if hasattr(Device, 'registration_type'):
        fields_to_select.append('registration_type')

    devices = Device.objects.select_related('added_by').only(*fields_to_select).order_by('-created_at')

    result_page = paginator.paginate_queryset(devices, request)
    serializer = DeviceSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


# ✅ Retrieve, Update, or Delete a Specific Device - No changes needed
@swagger_auto_schema(
    method='get',
    responses={200: DeviceSerializer},
    operation_description="Retrieve details of a specific device by ID."
)
@swagger_auto_schema(
    method='put',
    request_body=DeviceSerializer,
    responses={200: DeviceSerializer, 400: 'Validation Error'},
    operation_description="Update a specific device. Requires authentication."
)
@swagger_auto_schema(
    method='delete',
    responses={200: 'Device deleted successfully', 404: 'Device not found'},
    operation_description="Delete a specific device. Requires authentication."
)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def device_detail(request, pk):
    try:
        device = Device.objects.get(pk=pk)
    except Device.DoesNotExist:
        return Response({'error': 'Device not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(DeviceSerializer(device).data)

    elif request.method == 'PUT':
        serializer = DeviceSerializer(device, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        device.delete()
        return Response({'message': 'Device deleted successfully'})


# ✅ Register Device (Open for ESP32 or IoT device registration) - No changes needed
@swagger_auto_schema(
    method='post',
    request_body=DeviceSerializer,
    responses={201: DeviceSerializer, 400: 'Validation Error'},
    operation_description="Registers a device (e.g., from ESP32) when it connects to WiFi. Open to unauthenticated requests."
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register_device(request):
    serializer = DeviceSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ✅ Enhanced Register Device via WiFi (Unauthenticated)
@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'device_id': openapi.Schema(type=openapi.TYPE_STRING, description='MAC address from ESP32'),
            'name': openapi.Schema(type=openapi.TYPE_STRING, description='Device name'),
            'floor_number': openapi.Schema(type=openapi.TYPE_INTEGER, description='Floor number'),
            'room_number': openapi.Schema(type=openapi.TYPE_STRING, description='Room number'),
            # WiFi-specific fields that will be stored in metadata if available
            'model': openapi.Schema(type=openapi.TYPE_STRING, description='Device model'),
            'firmware_version': openapi.Schema(type=openapi.TYPE_STRING, description='Firmware version'),
            'ip_address': openapi.Schema(type=openapi.TYPE_STRING, description='Device IP'),
            'mac_address': openapi.Schema(type=openapi.TYPE_STRING, description='MAC address'),
            'signal_strength': openapi.Schema(type=openapi.TYPE_INTEGER, description='WiFi signal'),
        },
        required=['device_id']
    ),
    responses={
        201: DeviceSerializer,
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING),
                'device': openapi.Schema(type=openapi.TYPE_OBJECT),
            }
        ),
        400: 'Validation Error'
    },
    operation_description="Register a new device via WiFi using device_id. Returns existing device if already registered."
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register_device_via_wifi(request):
    """
    Called from the Expo app when connected to ESP32 device.
    Accepts: name, floor_number, room_number, device_id
    Additional optional: model, firmware_version (stored in metadata if field exists)
    """
    device_id = request.data.get("device_id")
    
    if not device_id:
        return Response({"error": "device_id is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Normalize device_id (remove colons if MAC address)
    device_id = device_id.upper().replace(':', '').replace('-', '')
    
    # Check for existing device
    try:
        existing_device = Device.objects.get(device_id=device_id)
        
        # If metadata field exists, update it
        if hasattr(Device, 'metadata'):
            metadata = existing_device.metadata or {}
            metadata.update({
                'model': request.data.get('model', metadata.get('model', 'ESP32')),
                'firmware_version': request.data.get('firmware_version', metadata.get('firmware_version', '1.0.0')),
                'ip_address': request.data.get('ip_address', metadata.get('ip_address')),
                'mac_address': request.data.get('mac_address', metadata.get('mac_address')),
                'signal_strength': request.data.get('signal_strength', metadata.get('signal_strength')),
                'last_connection': timezone.now().isoformat()
            })
            existing_device.metadata = metadata
            existing_device.save()
        
        logger.info(f"Device {device_id} attempted to re-register. Returning existing device.")
        
        return Response({
            "message": "Device already registered",
            "device": DeviceSerializer(existing_device).data
        }, status=status.HTTP_200_OK)
        
    except Device.DoesNotExist:
        # Device doesn't exist, create new one
        pass
    
    # Prepare base device data
    device_data = {
        'device_id': device_id,
        'name': request.data.get('name', f"ESP32_{device_id[-4:]}"),
        'room_number': request.data.get('room_number', ''),
        'floor_number': request.data.get('floor_number', 0),
    }
    
    # Validate floor_number
    try:
        device_data['floor_number'] = int(device_data['floor_number'])
    except (ValueError, TypeError):
        device_data['floor_number'] = 0
    
    # Create the device
    serializer = DeviceSerializer(data=device_data)
    if serializer.is_valid():
        save_kwargs = {}
        
        # Add registration_type if field exists
        if hasattr(Device, 'registration_type'):
            save_kwargs['registration_type'] = 'wifi'
        
        # Add metadata if field exists
        if hasattr(Device, 'metadata'):
            metadata = {
                'model': request.data.get('model', 'ESP32'),
                'firmware_version': request.data.get('firmware_version', '1.0.0'),
                'ip_address': request.data.get('ip_address'),
                'mac_address': request.data.get('mac_address', device_id),
                'signal_strength': request.data.get('signal_strength'),
                'registration_time': timezone.now().isoformat(),
                'registration_ip': request.META.get('REMOTE_ADDR')
            }
            save_kwargs['metadata'] = metadata
        
        device = serializer.save(**save_kwargs)
        
        logger.info(
            f"New device registered via WiFi: {device_id}",
            extra={
                'device_id': device_id,
                'model': request.data.get('model', 'Unknown'),
                'firmware_version': request.data.get('firmware_version', 'Unknown'),
                'ip': request.META.get('REMOTE_ADDR', 'Unknown')
            }
        )
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ✅ Additional endpoint to check device status
@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'device_id': openapi.Schema(type=openapi.TYPE_STRING, description='Device ID to check'),
        },
        required=['device_id']
    ),
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'exists': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                'device': openapi.Schema(type=openapi.TYPE_OBJECT),
            }
        )
    },
    operation_description="Check if a device is already registered"
)
@api_view(['POST'])
@permission_classes([AllowAny])
def check_device_status(request):
    """Check if a device with given device_id exists"""
    device_id = request.data.get('device_id')
    
    if not device_id:
        return Response(
            {"error": "device_id is required"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
        # Normalize device_id
    device_id = device_id.upper().replace(':', '').replace('-', '')
    
    try:
        device = Device.objects.get(device_id=device_id)
        serializer = DeviceSerializer(device)
        return Response({
            "exists": True,
            "device": serializer.data
        })
    except Device.DoesNotExist:
        return Response({
            "exists": False,
            "device": None
        })


# ✅ Update device from ESP32 (heartbeat/status update)
@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'device_id': openapi.Schema(type=openapi.TYPE_STRING, description='Device ID'),
            'ip_address': openapi.Schema(type=openapi.TYPE_STRING, description='Current IP'),
            'signal_strength': openapi.Schema(type=openapi.TYPE_INTEGER, description='WiFi signal'),
            'uptime': openapi.Schema(type=openapi.TYPE_INTEGER, description='Uptime in seconds'),
            'free_heap': openapi.Schema(type=openapi.TYPE_INTEGER, description='Free memory'),
        },
        required=['device_id']
    ),
    responses={
        200: 'Status updated',
        404: 'Device not found'
    },
    operation_description="Update device status (called by ESP32 devices)"
)
@api_view(['POST'])
@permission_classes([AllowAny])
def update_device_status(request):
    """ESP32 devices can call this to update their status"""
    device_id = request.data.get('device_id')
    
    if not device_id:
        return Response({"error": "device_id is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Normalize device_id
    device_id = device_id.upper().replace(':', '').replace('-', '')
    
    try:
        device = Device.objects.get(device_id=device_id)
        
        # Update metadata if field exists
        if hasattr(Device, 'metadata'):
            metadata = device.metadata or {}
            metadata.update({
                'last_heartbeat': timezone.now().isoformat(),
                'ip_address': request.data.get('ip_address', metadata.get('ip_address')),
                'signal_strength': request.data.get('signal_strength', metadata.get('signal_strength')),
                'uptime': request.data.get('uptime'),
                'free_heap': request.data.get('free_heap'),
            })
            device.metadata = metadata
            device.save()
        
        logger.info(f"Device {device_id} status updated")
        
        return Response({"message": "Status updated successfully"})
        
    except Device.DoesNotExist:
        return Response({"error": "Device not found"}, status=status.HTTP_404_NOT_FOUND)