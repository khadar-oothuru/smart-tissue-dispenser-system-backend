# Generated by Django 5.2.1 on 2025-06-02 17:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_customuser_otp_code_customuser_otp_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='otp_created_at',
            field=models.DateTimeField(blank=True, db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='username',
            field=models.CharField(blank=True, max_length=150, null=True, unique=True),
        ),
    ]
