from rest_framework import serializers
from device.models import Device

class DeviceSerializer(serializers.ModelSerializer):
    added_by = serializers.ReadOnlyField(source='added_by.id')  # Read-only user ID

    class Meta:
        model = Device
        fields = '__all__'
