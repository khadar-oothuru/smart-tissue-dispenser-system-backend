from django.urls import path

from .views.device_views import add_device, get_devices, device_detail
from .views.data_views import receive_device_data, all_device_data, device_data_by_id
from .views.notification_views import get_notifications, register_push_token
from .views.analytics_views import device_analytics, advanced_analytics

urlpatterns = [
    path('devices/', get_devices, name='get_devices'),
    path('devices/add/', add_device, name='add_device'),
    path('devices/<int:pk>/', device_detail, name='device_detail'),

    path('device-data/submit/', receive_device_data, name='receive_device_data'),
    path('device-data/all/', all_device_data, name='all_device_data'),
    path('device-data/<int:device_id>/', device_data_by_id, name='device_data_by_id'),

    path('notifications/', get_notifications, name='get_notifications'),
    path('device-analytics/', device_analytics, name='device_analytics'),
    path('expo-token/register/', register_push_token, name='register_push_token'),
    path('device-analytics/advanced/', advanced_analytics, name='advanced_analytics'),
]
