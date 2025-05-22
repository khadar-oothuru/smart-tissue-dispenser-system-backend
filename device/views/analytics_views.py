from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from django.db.models import Max

from device.models import Device, DeviceData

@swagger_auto_schema(
    method='get',
    responses={200: openapi.Response('Analytics per device')},
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


@swagger_auto_schema(
    method='get',
    responses={200: openapi.Response('Advanced analytics per device')},
    operation_description="Advanced analytics: total entries, low alerts, tamper counts, last alert timestamp"
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def advanced_analytics(request):
    data = []
    devices = Device.objects.all()
    for device in devices:
        device_data = DeviceData.objects.filter(device=device)
        low_alerts = device_data.filter(alert="LOW").count()
        tamper_count = device_data.filter(tamper=True).count()
        total_data = device_data.count()
        last_alert = device_data.aggregate(Max('timestamp'))['timestamp__max']

        data.append({
            "device_id": device.id,
            "room": device.room_number,
            "floor": device.floor_number,
            "total_entries": total_data,
            "low_alert_count": low_alerts,
            "tamper_count": tamper_count,
            "last_alert_time": last_alert
        })
    return Response(data)
