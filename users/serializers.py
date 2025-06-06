from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser
import cloudinary
import cloudinary.uploader

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

    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
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

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'profile_picture']
        read_only_fields = ['email']  # Email cannot be changed

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])

class ProfilePictureSerializer(serializers.Serializer):
    image = serializers.ImageField(required=True)

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'role': self.user.role,
            'profile_picture': self.user.profile_picture,
        }
        return data