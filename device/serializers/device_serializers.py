
# from rest_framework import serializers
# from ..models import Device


# class DeviceSerializer(serializers.ModelSerializer):
#     added_by_username = serializers.CharField(source='added_by.username', read_only=True)
    
#     class Meta:
#         model = Device
#         fields = ['id', 'name', 'device_id', 'room_number', 'floor_number', 'added_by', 'added_by_username', 'created_at']
#         read_only_fields = ['created_at', 'added_by']


# device/serializers/device_serializers.py
from rest_framework import serializers
from ..models import Device

class DeviceSerializer(serializers.ModelSerializer):
    added_by_username = serializers.CharField(source='added_by.username', read_only=True)
    # Make these read-only from metadata
    model = serializers.SerializerMethodField()
    firmware_version = serializers.SerializerMethodField()
    
    class Meta:
        model = Device
        fields = ['id', 'name', 'device_id', 'room_number', 'floor_number', 
                  'registration_type', 'metadata', 'added_by', 'added_by_username', 
                  'created_at', 'model', 'firmware_version']
        read_only_fields = ['created_at', 'added_by', 'registration_type']
    
    def get_model(self, obj):
        return obj.metadata.get('model', 'N/A') if obj.metadata else 'N/A'
    
    def get_firmware_version(self, obj):
        return obj.metadata.get('firmware_version', 'N/A') if obj.metadata else 'N/A'