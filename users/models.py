from django.contrib.auth.models import AbstractUser
from django.db import models

def default_profile_image():
    return 'https://images.unsplash.com/photo-1542190891-2093d38760f2?q=80&w=3387&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D'

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    email = models.EmailField(unique=True)
    profile_picture = models.URLField(blank=True, null=True, default=default_profile_image)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email
