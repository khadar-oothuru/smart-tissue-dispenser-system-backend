from django.urls import path
from . import views

urlpatterns = [
    # Device Management
    path('devices/', views.get_devices, name='get_devices'),
    path('devices/add/', views.add_device, name='add_device'),
    path('devices/<int:pk>/', views.device_detail, name='device_detail'),

    # Device Data
    path('device-data/submit/', views.receive_device_data, name='receive_device_data'),
    path('device-data/all/', views.all_device_data, name='all_device_data'),
    path('device-data/<int:device_id>/', views.device_data_by_id, name='device_data_by_id'),

    # Notifications & Analytics
    path('notifications/', views.get_notifications, name='get_notifications'),
    path('device-analytics/', views.device_analytics, name='device_analytics'),
]
