from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    profile_picture = serializers.URLField(required=False, allow_null=True)
    role = serializers.ChoiceField(choices=[('user', 'User'), ('admin', 'Admin')], default='user', required=False)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password', 'role', 'profile_picture')

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        profile_picture = validated_data.pop('profile_picture', None)
        role = validated_data.get('role', 'user')
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=role
        )
        if profile_picture:
            user.profile_picture = profile_picture
            user.save()
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'role', 'profile_picture']

# Placeholder for your custom token serializer, implement as needed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    # override methods here if needed, otherwise just inherit as is
    pass
