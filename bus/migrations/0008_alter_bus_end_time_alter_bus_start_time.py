# Generated by Django 4.0.5 on 2022-08-02 22:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bus', '0007_bus_transit_log_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bus',
            name='end_time',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='bus',
            name='start_time',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
    ]