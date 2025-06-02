
# from django.urls import path

# from .views.device_views import add_device, get_devices, device_detail
# from .views.data_views import receive_device_data, all_device_data, device_data_by_id
# from .views.notification_views import (
#     get_notifications, 
#     register_push_token,
#     delete_notification,
#     mark_notification_as_read,
#     clear_all_notifications,
#     get_unread_count
# )
# from .views.analytics_views import (
#     device_analytics, 
#     advanced_analytics,
#     device_realtime_status, 
#     time_based_analytics, 
#     download_analytics,
#     summary_analytics,
#     device_status_summary,
# )
# from .views.device_views import register_device, register_device_via_wifi

# urlpatterns = [
#     # Device endpoints
#     path('devices/', get_devices, name='get_devices'),
#     path('devices/add/', add_device, name='add_device'),
#     path('devices/<int:pk>/', device_detail, name='device_detail'),

#     # Device data endpoints
#     path('device-data/submit/', receive_device_data, name='receive_device_data'),
#     path('device-data/all/', all_device_data, name='all_device_data'),
#     path('device-data/<int:device_id>/', device_data_by_id, name='device_data_by_id'),

#     # Notification endpoints
#     path('notifications/', get_notifications, name='get_notifications'),
#     path('notifications/<int:pk>/', delete_notification, name='delete_notification'),
#     path('notifications/<int:pk>/mark-read/', mark_notification_as_read, name='mark_notification_as_read'),
#     path('notifications/clear-all/', clear_all_notifications, name='clear_all_notifications'),
#     path('notifications/unread-count/', get_unread_count, name='get_unread_count'),
#     path('expo-token/register/', register_push_token, name='register_push_token'),

#     # Analytics endpoints
#     # path('device-analytics/', device_analytics, name='device_analytics'),
#     # path('device-analytics/advanced/', advanced_analytics, name='advanced_analytics'),
#     path('device-analytics/', advanced_analytics, name='advanced_analytics'),
#     path('device-analytics/time-based/', time_based_analytics, name='time_based_analytics'),
#     path('device-analytics/download/', download_analytics, name='download_analytics'),
#     path('device-analytics/summary/', summary_analytics, name='summary_analytics'),
#     path('device-analytics/realtime-status/', device_realtime_status, name='device_realtime_status'),
#     path('device-analytics/status-summary/', device_status_summary, name='device_status_summary'),
    
#     # Device registration
#     path('device/register/', register_device),
#     path('wifi/', register_device_via_wifi)
# ]



# device/urls.py
from django.urls import path

from .views.device_views import (
    add_device, 
    get_devices, 
    device_detail,
    register_device, 
    register_device_via_wifi,
    check_device_status,
    update_device_status
)
from .views.data_views import receive_device_data, all_device_data, device_data_by_id
from .views.notification_views import (
    get_notifications, 
    register_push_token,
    delete_notification,
    mark_notification_as_read,
    clear_all_notifications,
    get_unread_count
)
from .views.analytics_views import (
    device_analytics, 
    advanced_analytics,
    device_realtime_status, 
    time_based_analytics, 
    download_analytics,
    summary_analytics,
    device_status_summary,
)

urlpatterns = [
    # Device endpoints
    path('devices/', get_devices, name='get_devices'),
    path('devices/add/', add_device, name='add_device'),
    path('devices/<int:pk>/', device_detail, name='device_detail'),

    # Device data endpoints
    path('device-data/submit/', receive_device_data, name='receive_device_data'),
    path('device-data/all/', all_device_data, name='all_device_data'),
    path('device-data/<int:device_id>/', device_data_by_id, name='device_data_by_id'),

    # Notification endpoints
    path('notifications/', get_notifications, name='get_notifications'),
    path('notifications/<int:pk>/', delete_notification, name='delete_notification'),
    path('notifications/<int:pk>/mark-read/', mark_notification_as_read, name='mark_notification_as_read'),
    path('notifications/clear-all/', clear_all_notifications, name='clear_all_notifications'),
    path('notifications/unread-count/', get_unread_count, name='get_unread_count'),
    path('expo-token/register/', register_push_token, name='register_push_token'),

    # Analytics endpoints
    path('device-analytics/', advanced_analytics, name='advanced_analytics'),
    path('device-analytics/time-based/', time_based_analytics, name='time_based_analytics'),
    path('device-analytics/download/', download_analytics, name='download_analytics'),
    path('device-analytics/summary/', summary_analytics, name='summary_analytics'),
    path('device-analytics/realtime-status/', device_realtime_status, name='device_realtime_status'),
    path('device-analytics/status-summary/', device_status_summary, name='device_status_summary'),
    
    # Device registration endpoints
    path('device/register/', register_device, name='register_device'),
    path('wifi/', register_device_via_wifi, name='register_device_via_wifi'),
    
    # New WiFi-related endpoints
    path('devices/check-status/', check_device_status, name='check_device_status'),
    path('devices/update-status/', update_device_status, name='update_device_status'),
]