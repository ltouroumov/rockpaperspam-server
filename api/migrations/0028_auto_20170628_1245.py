# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-06-28 12:45
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0027_auto_20170628_1245'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='template',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.NotificationTemplate'),
        ),
    ]