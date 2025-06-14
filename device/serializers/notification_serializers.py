
from rest_framework import serializers
from ..models import Notification, ExpoPushToken
from .device_serializers import DeviceSerializer


class NotificationSerializer(serializers.ModelSerializer):
    device = DeviceSerializer(read_only=True)
    device_id = serializers.IntegerField(source='device.id', read_only=True)
    type = serializers.CharField(source='notification_type', read_only=True)  # For frontend compatibility
    
    class Meta:
        model = Notification
        fields = [
            'id', 
            'device', 
            'device_id', 
            'message', 
            'title',
            'notification_type',
            'type',  # Frontend compatibility field
            'alert',
            'tamper',
            'priority',
            'is_read', 
            'created_at'
        ]
        read_only_fields = ['created_at', 'device_id', 'type']
    
    def to_representation(self, instance):
        """Ensure frontend compatibility with multiple type field names"""
        data = super().to_representation(instance)
        # Add multiple type fields for maximum compatibility
        notification_type = data.get('notification_type', 'info')
        data['type'] = notification_type
        data['alert_type'] = notification_type
        return data


class ExpoPushTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpoPushToken
        fields = ['id', 'user', 'token']
        read_only_fields = ['user']