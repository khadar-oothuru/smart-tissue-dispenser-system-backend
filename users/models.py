from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta
import random
import string

def default_profile_image():
    return 'https://images.unsplash.com/photo-1542190891-2093d38760f2?q=80&w=3387&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D'

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User'),
    )

    # Override fields
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    profile_picture = models.URLField(blank=True, null=True, default=default_profile_image)

    # OTP Fields
    otp_code = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True, db_index=True)
    otp_verified = models.BooleanField(default=False)

    # Set email as the login field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def generate_otp(self):
        """Generate a 6-digit numeric OTP and save with timestamp"""
        self.otp_code = ''.join(random.choices(string.digits, k=6))
        self.otp_created_at = timezone.now()
        self.otp_verified = False
        self.save()
        return self.otp_code
    


    def verify_otp(self, otp):
    
        if not self.otp_code or not self.otp_created_at:
            return False

        expiry_time = self.otp_created_at + timedelta(minutes=10)
        if timezone.now() > expiry_time:
            return False

        if self.otp_code == otp:
        # Set otp_verified to True when OTP matches
            self.otp_verified = True
            self.save()
            return True

        return False

    # def verify_otp(self, otp):
    #     """
    #     Verify the provided OTP:
    #     - Must match the stored OTP
    #     - Must not be expired (10-minute validity)
    #     """
    #     if not self.otp_code or not self.otp_created_at:
    #         return False

    #     expiry_time = self.otp_created_at + timedelta(minutes=10)
    #     if timezone.now() > expiry_time:
    #         return False

    #     if self.otp_code == otp:
    #         return True

    #     return False

    

    def clear_otp(self):
        """Clear OTP data after successful use"""
        self.otp_code = None
        self.otp_created_at = None
        self.otp_verified = False
        self.save()

    def is_otp_valid(self):
        """Check if the current OTP is still valid (within 10 minutes)"""
        if not self.otp_created_at:
            return False
        return timezone.now() <= self.otp_created_at + timedelta(minutes=10)

    def __str__(self):
        return f"{self.email} - Role: {self.role}"