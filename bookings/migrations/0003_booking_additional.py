# Generated by Django 3.2.18 on 2023-05-01 18:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0002_rename_email_booking_user_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='additional',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]