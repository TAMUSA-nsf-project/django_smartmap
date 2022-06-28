# Generated by Django 4.0.5 on 2022-06-28 21:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('bus', '0003_busroute_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='BusDriver',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': [('access_busdriver_pages', 'Can access bus driver pages.')],
            },
        ),
    ]
