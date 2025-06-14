from .device_views import add_device, get_devices, device_detail
from .data_views import receive_device_data, all_device_data, device_data_by_id
from .notification_views import get_notifications, register_push_token
from .analytics_views import device_analytics, advanced_analytics 


__all__ = [
    'add_device',
    'get_devices',
    'device_detail',
    'receive_device_data',
    'all_device_data',
    'device_data_by_id',
    'get_notifications',
    'register_push_token',
    'device_analytics',
    'advanced_analytics',
]
