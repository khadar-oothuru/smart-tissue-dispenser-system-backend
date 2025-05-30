# Generated by Django 5.2.1 on 2025-05-16 15:19

import users.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_customuser_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='profile_picture',
            field=models.URLField(blank=True, default=users.models.default_profile_image, null=True),
        ),
    ]
