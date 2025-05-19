from rest_framework import serializers
from .models import Device, DeviceData, Notification

class DeviceSerializer(serializers.ModelSerializer):
    added_by = serializers.ReadOnlyField(source='added_by.id')  # Make added_by read-only, show user id

    class Meta:
        model = Device
        fields = '__all__'

class DeviceDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceData
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
