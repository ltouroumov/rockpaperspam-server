# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-06-28 08:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0022_auto_20170628_0827'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='read',
            field=models.BooleanField(default=False),
        ),
    ]
