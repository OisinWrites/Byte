# Generated by Django 3.2.18 on 2023-05-04 12:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0019_booking_booking_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='tableavailability',
            name='id_of_booking',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
