# Generated by Django 4.0.5 on 2022-07-18 16:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bus', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bus',
            name='route',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='bus.busroute'),
        ),
    ]
