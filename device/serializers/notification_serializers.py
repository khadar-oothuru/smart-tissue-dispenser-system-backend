
from rest_framework import serializers
from ..models import Notification, ExpoPushToken
from .device_serializers import DeviceSerializer


class NotificationSerializer(serializers.ModelSerializer):
    device = DeviceSerializer(read_only=True)
    device_id = serializers.IntegerField(source='device.id', read_only=True)
    
    class Meta:
        model = Notification
        fields = ['id', 'device', 'device_id', 'message', 'title', 'alert', 'tamper', 'is_read', 'created_at']
        read_only_fields = ['created_at']


class ExpoPushTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpoPushToken
        fields = ['id', 'user', 'token']
        read_only_fields = ['user']