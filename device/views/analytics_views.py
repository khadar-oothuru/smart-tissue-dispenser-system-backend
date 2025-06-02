# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from drf_yasg.utils import swagger_auto_schema
# from drf_yasg import openapi
# from django.http import HttpResponse
# from django.db.models import Max, Count, Q
# from django.utils import timezone
# from datetime import datetime, timedelta
# import csv
# import json

# from device.models import Device, DeviceData

# @swagger_auto_schema(
#     method='get',
#     responses={200: openapi.Response('Analytics per device')},
#     operation_description="Get analytics like LOW alerts and last alert timestamp for each device"
# )
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def device_analytics(request):
#     devices = Device.objects.all()
#     analytics = []

#     for device in devices:
#         low_alerts = DeviceData.objects.filter(device=device, alert="LOW").count()
#         last_entry = DeviceData.objects.filter(device=device).order_by('-timestamp').first()
#         analytics.append({
#             "device_id": device.id,
#             "room": device.room_number,
#             "floor": device.floor_number,
#             "low_alert_count": low_alerts,
#             "last_alert_time": last_entry.timestamp if last_entry else None
#         })

#     return Response(analytics)


# @swagger_auto_schema(
#     method='get',
#     responses={200: openapi.Response('Advanced analytics per device')},
#     operation_description="Advanced analytics: total entries, low alerts, tamper counts, last alert timestamp"
# )
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def advanced_analytics(request):
#     data = []
#     devices = Device.objects.all()
#     for device in devices:
#         device_data = DeviceData.objects.filter(device=device)
#         low_alerts = device_data.filter(alert="LOW").count()
#         # Fix: Filter for string "true" instead of boolean True
#         tamper_count = device_data.filter(tamper="true").count()  # Changed this line
#         total_data = device_data.count()
#         last_alert = device_data.aggregate(Max('timestamp'))['timestamp__max']

#         data.append({
#             "device_id": device.id,
#             "room": device.room_number,
#             "floor": device.floor_number,
#             "total_entries": total_data,
#             "low_alert_count": low_alerts,
#             "tamper_count": tamper_count,
#             "last_alert_time": last_alert
#         })
#     return Response(data)


# @swagger_auto_schema(
#     method='get',
#     manual_parameters=[
#         openapi.Parameter('period', openapi.IN_QUERY, description="Period: weekly, monthly, quarterly, yearly", type=openapi.TYPE_STRING),
#         openapi.Parameter('device_id', openapi.IN_QUERY, description="Specific device ID (optional)", type=openapi.TYPE_INTEGER),
#     ],
#     responses={200: openapi.Response('Time-based analytics')},
#     operation_description="Get analytics data for different time periods"
# )
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def time_based_analytics(request):
#     period = request.GET.get('period', 'weekly')
#     device_id = request.GET.get('device_id')
    
#     now = timezone.now()
    
#     # Calculate date ranges based on period
#     if period == 'weekly':
#         start_date = now - timedelta(weeks=12)  # Last 12 weeks
#         date_format = '%Y-W%U'
#         period_name = 'Week'
#     elif period == 'monthly':
#         start_date = now - timedelta(days=365)  # Last 12 months
#         date_format = '%Y-%m'
#         period_name = 'Month'
#     elif period == 'quarterly':
#         start_date = now - timedelta(days=365*2)  # Last 8 quarters
#         date_format = '%Y-Q'
#         period_name = 'Quarter'
#     elif period == 'yearly':
#         start_date = now - timedelta(days=365*5)  # Last 5 years
#         date_format = '%Y'
#         period_name = 'Year'
#     else:
#         return Response({'error': 'Invalid period'}, status=400)
    
#     # Filter devices
#     devices = Device.objects.all()
#     if device_id:
#         devices = devices.filter(id=device_id)
    
#     analytics_data = []
    
#     for device in devices:
#         device_data = DeviceData.objects.filter(
#             device=device,
#             timestamp__gte=start_date
#         ).order_by('timestamp')
        
#         # Group data by time periods
#         period_data = {}
        
#         for data_point in device_data:
#             if period == 'quarterly':
#                 quarter = f"{data_point.timestamp.year}-Q{((data_point.timestamp.month-1)//3)+1}"
#                 period_key = quarter
#             else:
#                 period_key = data_point.timestamp.strftime(date_format)
            
#             if period_key not in period_data:
#                 period_data[period_key] = {
#                     'total_entries': 0,
#                     'low_alerts': 0,
#                     'tamper_alerts': 0,
#                     'high_alerts': 0,
#                     'medium_alerts': 0
#                 }
            
#             period_data[period_key]['total_entries'] += 1
            
#             if data_point.alert == 'LOW':
#                 period_data[period_key]['low_alerts'] += 1
#             elif data_point.alert == 'HIGH':
#                 period_data[period_key]['high_alerts'] += 1
#             elif data_point.alert == 'MEDIUM':
#                 period_data[period_key]['medium_alerts'] += 1
                
#             if data_point.tamper:
#                 period_data[period_key]['tamper_alerts'] += 1
        
#         # Convert to list format
#         periods = []
#         for period_key, data in sorted(period_data.items()):
#             periods.append({
#                 'period': period_key,
#                 'period_name': f"{period_name} {period_key}",
#                 **data
#             })
        
#         analytics_data.append({
#             'device_id': device.id,
#             'room': device.room_number,
#             'floor': device.floor_number,
#             'device_name': getattr(device, 'name', f'Device {device.id}'),
#             'periods': periods
#         })
    
#     return Response({
#         'period_type': period,
#         'data': analytics_data
#     })


# @swagger_auto_schema(
#     method='get',
#     manual_parameters=[
#         openapi.Parameter('period', openapi.IN_QUERY, description="Period: weekly, monthly, quarterly, yearly", type=openapi.TYPE_STRING),
#         openapi.Parameter('device_id', openapi.IN_QUERY, description="Specific device ID (optional)", type=openapi.TYPE_INTEGER),
#         openapi.Parameter('format', openapi.IN_QUERY, description="Download format: csv or json", type=openapi.TYPE_STRING),
#     ],
#     responses={200: openapi.Response('Download analytics data')},
#     operation_description="Download analytics data in CSV or JSON format"
# )
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def download_analytics(request):
#     period = request.GET.get('period', 'weekly')
#     device_id = request.GET.get('device_id')
#     format_type = request.GET.get('format', 'csv')
    
#     # Get the same data as time_based_analytics
#     request_copy = request._request if hasattr(request, '_request') else request
#     request_copy.GET = request.GET
    
#     # Get analytics data
#     analytics_response = time_based_analytics(request)
#     analytics_data = analytics_response.data
    
#     filename = f"analytics_{period}_{timezone.now().strftime('%Y%m%d_%H%M%S')}"
    
#     if format_type == 'csv':
#         response = HttpResponse(content_type='text/csv')
#         response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
        
#         writer = csv.writer(response)
        
#         # Write headers
#         writer.writerow([
#             'Device ID', 'Room', 'Floor', 'Device Name', 'Period', 
#             'Total Entries', 'Low Alerts', 'High Alerts', 'Medium Alerts', 'Tamper Alerts'
#         ])
        
#         # Write data
#         for device_data in analytics_data['data']:
#             for period_data in device_data['periods']:
#                 writer.writerow([
#                     device_data['device_id'],
#                     device_data['room'],
#                     device_data['floor'],
#                     device_data['device_name'],
#                     period_data['period_name'],
#                     period_data['total_entries'],
#                     period_data['low_alerts'],
#                     period_data['high_alerts'],
#                     period_data['medium_alerts'],
#                     period_data['tamper_alerts']
#                 ])
        
#         return response
    
#     elif format_type == 'json':
#         response = HttpResponse(
#             json.dumps(analytics_data, indent=2, default=str),
#             content_type='application/json'
#         )
#         response['Content-Disposition'] = f'attachment; filename="{filename}.json"'
#         return response
    
#     else:
#         return Response({'error': 'Invalid format type'}, status=400)


# @swagger_auto_schema(
#     method='get',
#     responses={200: openapi.Response('Summary analytics for dashboard')},
#     operation_description="Get summary analytics for dashboard display"
# )
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def summary_analytics(request):
#     now = timezone.now()
    
#     # Overall stats
#     total_devices = Device.objects.count()
#     total_entries = DeviceData.objects.count()
    
#     # Recent activity (last 24 hours)
#     last_24h = now - timedelta(hours=24)
#     recent_entries = DeviceData.objects.filter(timestamp__gte=last_24h).count()
#     recent_alerts = DeviceData.objects.filter(
#         timestamp__gte=last_24h,
#         alert__in=['LOW', 'HIGH', 'MEDIUM']
#     ).count()
    
#     # Alert distribution (all time)
#     alert_distribution = {
#         'low': DeviceData.objects.filter(alert='LOW').count(),
#         'medium': DeviceData.objects.filter(alert='MEDIUM').count(),
#         'high': DeviceData.objects.filter(alert='HIGH').count(),
#         'tamper': DeviceData.objects.filter(tamper=True).count()
#     }
    
#     # Most active devices (last 7 days)
#     last_week = now - timedelta(days=7)
#     active_devices = DeviceData.objects.filter(
#         timestamp__gte=last_week
#     ).values('device__id', 'device__room_number', 'device__floor_number').annotate(
#         entry_count=Count('id')
#     ).order_by('-entry_count')[:5]
    
#     return Response({
#         'summary': {
#             'total_devices': total_devices,
#             'total_entries': total_entries,
#             'recent_entries_24h': recent_entries,
#             'recent_alerts_24h': recent_alerts
#         },
#         'alert_distribution': alert_distribution,
#         'most_active_devices': list(active_devices)
#     })


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.http import HttpResponse
from django.db.models import Max, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
import csv
import json

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
        # Fix: Filter for string "true" instead of boolean True
        tamper_count = device_data.filter(tamper="true").count()  # Changed this line
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


@swagger_auto_schema(
    method='get',
    responses={200: openapi.Response('Real-time device status')},
    operation_description="Get current/latest status of all devices (real-time data)"
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def device_realtime_status(request):
    """
    Returns the current status of each device based on the latest data entry.
    This data changes as new data comes in from devices.
    """
    devices = Device.objects.all()
    realtime_data = []
    
    for device in devices:
        # Get the latest data entry for this device
        latest_data = DeviceData.objects.filter(device=device).order_by('-timestamp').first()
        
        if latest_data:
            # Calculate time since last update
            time_since_update = timezone.now() - latest_data.timestamp
            minutes_since_update = int(time_since_update.total_seconds() / 60)
            
            # Determine if device is active/online (updated within last 5 minutes)
            is_active = minutes_since_update <= 5
            
            # Determine current status based on latest data
            current_status = "normal"
            status_priority = 0
            
            # Check current conditions
            if latest_data.tamper == "true" and latest_data.alert == "LOW":
                current_status = "critical"
                status_priority = 3
            elif latest_data.tamper == "true":
                current_status = "tamper"
                status_priority = 2
            elif latest_data.alert == "LOW":
                current_status = "low"
                status_priority = 1
            elif latest_data.alert == "MEDIUM":
                current_status = "medium"
                status_priority = 0
            elif latest_data.alert == "HIGH":
                current_status = "high"
                status_priority = 0
                
            realtime_data.append({
                "device_id": device.id,
                "device_name": device.name,
                "room": device.room_number,
                "floor": device.floor_number,
                "is_active": is_active,
                "current_status": current_status,
                "status_priority": status_priority,
                "current_alert": latest_data.alert,
                "current_tamper": latest_data.tamper == "true",
                "current_count": latest_data.count,
                "last_updated": latest_data.timestamp,
                "minutes_since_update": minutes_since_update,
                "refer_val": latest_data.refer_val
            })
        else:
            # No data for this device yet
            realtime_data.append({
                "device_id": device.id,
                "device_name": device.name,
                "room": device.room_number,
                "floor": device.floor_number,
                "is_active": False,
                "current_status": "inactive",
                "status_priority": -1,
                "current_alert": None,
                "current_tamper": False,
                "current_count": 0,
                "last_updated": None,
                "minutes_since_update": None,
                "refer_val": None
            })
    
    # Sort by status priority (critical first) and then by last updated
    realtime_data.sort(key=lambda x: (-x['status_priority'], x['last_updated'] or ''), reverse=True)
    
    return Response(realtime_data)


@swagger_auto_schema(
    method='get',
    responses={200: openapi.Response('Device status summary')},
    operation_description="Get summary of current device statuses"
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def device_status_summary(request):
    """
    Returns a summary of device statuses for dashboard display
    """
    total_devices = Device.objects.count()
    now = timezone.now()
    
    # Get latest status for each device
    device_statuses = []
    for device in Device.objects.all():
        latest_data = DeviceData.objects.filter(device=device).order_by('-timestamp').first()
        if latest_data:
            time_since = now - latest_data.timestamp
            is_active = time_since.total_seconds() <= 300  # 5 minutes
            
            device_statuses.append({
                'device_id': device.id,
                'is_active': is_active,
                'alert': latest_data.alert,
                'tamper': latest_data.tamper == "true",
                'timestamp': latest_data.timestamp
            })
        else:
            device_statuses.append({
                'device_id': device.id,
                'is_active': False,
                'alert': None,
                'tamper': False,
                'timestamp': None
            })
    
    # Calculate summaries
    active_count = sum(1 for d in device_statuses if d['is_active'])
    critical_count = sum(1 for d in device_statuses if d['tamper'] and d['alert'] == 'LOW')
    low_alert_count = sum(1 for d in device_statuses if d['alert'] == 'LOW' and not d['tamper'])
    tamper_only_count = sum(1 for d in device_statuses if d['tamper'] and d['alert'] != 'LOW')
    normal_count = sum(1 for d in device_statuses if d['is_active'] and not d['tamper'] and d['alert'] not in ['LOW'])
    inactive_count = sum(1 for d in device_statuses if not d['is_active'])
    
    return Response({
        'summary': {
            'total_devices': total_devices,
            'active_devices': active_count,
            'inactive_devices': inactive_count,
            'critical_devices': critical_count,
            'low_alert_devices': low_alert_count,
            'tamper_only_devices': tamper_only_count,
            'normal_devices': normal_count
        },
        'status_breakdown': {
            'critical': critical_count,
            'low': low_alert_count,
            'tamper': tamper_only_count,
            'normal': normal_count,
            'inactive': inactive_count
        },
        'percentages': {
            'active_percentage': round((active_count / total_devices * 100), 1) if total_devices > 0 else 0,
            'critical_percentage': round((critical_count / total_devices * 100), 1) if total_devices > 0 else 0,
            'inactive_percentage': round((inactive_count / total_devices * 100), 1) if total_devices > 0 else 0
        },
        'last_updated': now
    })


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter('period', openapi.IN_QUERY, description="Period: weekly, monthly, quarterly, yearly", type=openapi.TYPE_STRING),
        openapi.Parameter('device_id', openapi.IN_QUERY, description="Specific device ID (optional)", type=openapi.TYPE_INTEGER),
    ],
    responses={200: openapi.Response('Time-based analytics')},
    operation_description="Get analytics data for different time periods"
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def time_based_analytics(request):
    period = request.GET.get('period', 'weekly')
    device_id = request.GET.get('device_id')
    
    now = timezone.now()
    
    # Calculate date ranges based on period
    if period == 'weekly':
        start_date = now - timedelta(weeks=12)  # Last 12 weeks
        date_format = '%Y-W%U'
        period_name = 'Week'
    elif period == 'monthly':
        start_date = now - timedelta(days=365)  # Last 12 months
        date_format = '%Y-%m'
        period_name = 'Month'
    elif period == 'quarterly':
        start_date = now - timedelta(days=365*2)  # Last 8 quarters
        date_format = '%Y-Q'
        period_name = 'Quarter'
    elif period == 'yearly':
        start_date = now - timedelta(days=365*5)  # Last 5 years
        date_format = '%Y'
        period_name = 'Year'
    else:
        return Response({'error': 'Invalid period'}, status=400)
    
    # Filter devices
    devices = Device.objects.all()
    if device_id:
        devices = devices.filter(id=device_id)
    
    analytics_data = []
    
    for device in devices:
        device_data = DeviceData.objects.filter(
            device=device,
            timestamp__gte=start_date
        ).order_by('timestamp')
        
        # Group data by time periods
        period_data = {}
        
        for data_point in device_data:
            if period == 'quarterly':
                quarter = f"{data_point.timestamp.year}-Q{((data_point.timestamp.month-1)//3)+1}"
                period_key = quarter
            else:
                period_key = data_point.timestamp.strftime(date_format)
            
            if period_key not in period_data:
                period_data[period_key] = {
                    'total_entries': 0,
                    'low_alerts': 0,
                    'tamper_alerts': 0,
                    'high_alerts': 0,
                    'medium_alerts': 0
                }
            
            period_data[period_key]['total_entries'] += 1
            
            if data_point.alert == 'LOW':
                                period_data[period_key]['low_alerts'] += 1
            elif data_point.alert == 'HIGH':
                period_data[period_key]['high_alerts'] += 1
            elif data_point.alert == 'MEDIUM':
                period_data[period_key]['medium_alerts'] += 1
                
            # Fix: Check for string "true" instead of boolean
            if data_point.tamper == "true":
                period_data[period_key]['tamper_alerts'] += 1
        
        # Convert to list format
        periods = []
        for period_key, data in sorted(period_data.items()):
            periods.append({
                'period': period_key,
                'period_name': f"{period_name} {period_key}",
                **data
            })
        
        analytics_data.append({
            'device_id': device.id,
            'room': device.room_number,
            'floor': device.floor_number,
            'device_name': getattr(device, 'name', f'Device {device.id}'),
            'periods': periods
        })
    
    return Response({
        'period_type': period,
        'data': analytics_data
    })


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter('period', openapi.IN_QUERY, description="Period: weekly, monthly, quarterly, yearly", type=openapi.TYPE_STRING),
        openapi.Parameter('device_id', openapi.IN_QUERY, description="Specific device ID (optional)", type=openapi.TYPE_INTEGER),
        openapi.Parameter('format', openapi.IN_QUERY, description="Download format: csv or json", type=openapi.TYPE_STRING),
    ],
    responses={200: openapi.Response('Download analytics data')},
    operation_description="Download analytics data in CSV or JSON format"
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_analytics(request):
    period = request.GET.get('period', 'weekly')
    device_id = request.GET.get('device_id')
    format_type = request.GET.get('format', 'csv')
    
    # Get the same data as time_based_analytics
    request_copy = request._request if hasattr(request, '_request') else request
    request_copy.GET = request.GET
    
    # Get analytics data
    analytics_response = time_based_analytics(request)
    analytics_data = analytics_response.data
    
    filename = f"analytics_{period}_{timezone.now().strftime('%Y%m%d_%H%M%S')}"
    
    if format_type == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
        
        writer = csv.writer(response)
        
        # Write headers
        writer.writerow([
            'Device ID', 'Room', 'Floor', 'Device Name', 'Period', 
            'Total Entries', 'Low Alerts', 'High Alerts', 'Medium Alerts', 'Tamper Alerts'
        ])
        
        # Write data
        for device_data in analytics_data['data']:
            for period_data in device_data['periods']:
                writer.writerow([
                    device_data['device_id'],
                    device_data['room'],
                    device_data['floor'],
                    device_data['device_name'],
                    period_data['period_name'],
                    period_data['total_entries'],
                    period_data['low_alerts'],
                    period_data['high_alerts'],
                    period_data['medium_alerts'],
                    period_data['tamper_alerts']
                ])
        
        return response
    
    elif format_type == 'json':
        response = HttpResponse(
            json.dumps(analytics_data, indent=2, default=str),
            content_type='application/json'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}.json"'
        return response
    
    else:
        return Response({'error': 'Invalid format type'}, status=400)


@swagger_auto_schema(
    method='get',
    responses={200: openapi.Response('Summary analytics for dashboard')},
    operation_description="Get summary analytics for dashboard display"
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def summary_analytics(request):
    now = timezone.now()
    
    # Overall stats
    total_devices = Device.objects.count()
    total_entries = DeviceData.objects.count()
    
    # Recent activity (last 24 hours)
    last_24h = now - timedelta(hours=24)
    recent_entries = DeviceData.objects.filter(timestamp__gte=last_24h).count()
    recent_alerts = DeviceData.objects.filter(
        timestamp__gte=last_24h,
        alert__in=['LOW', 'HIGH', 'MEDIUM']
    ).count()
    
    # Alert distribution (all time) - Fixed to use string "true"
    alert_distribution = {
        'low': DeviceData.objects.filter(alert='LOW').count(),
        'medium': DeviceData.objects.filter(alert='MEDIUM').count(),
        'high': DeviceData.objects.filter(alert='HIGH').count(),
        'tamper': DeviceData.objects.filter(tamper="true").count()  # Fixed this line
    }
    
    # Most active devices (last 7 days)
    last_week = now - timedelta(days=7)
    active_devices = DeviceData.objects.filter(
        timestamp__gte=last_week
    ).values('device__id', 'device__room_number', 'device__floor_number').annotate(
        entry_count=Count('id')
    ).order_by('-entry_count')[:5]
    
    return Response({
        'summary': {
            'total_devices': total_devices,
            'total_entries': total_entries,
            'recent_entries_24h': recent_entries,
            'recent_alerts_24h': recent_alerts
        },
        'alert_distribution': alert_distribution,
        'most_active_devices': list(active_devices)
    })