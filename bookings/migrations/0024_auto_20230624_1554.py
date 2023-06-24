# Generated by Django 3.2 on 2023-06-24 15:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0023_alter_tableavailability_table'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='table',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='bookings.table'),
        ),
        migrations.AlterField(
            model_name='tableavailability',
            name='table',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='bookings.table'),
            preserve_default=False,
        ),
    ]