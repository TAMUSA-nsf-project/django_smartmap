# Generated by Django 3.2.13 on 2022-07-01 18:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bus', '0006_bus'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bus',
            name='driver',
            field=models.CharField(max_length=100),
        ),
    ]
