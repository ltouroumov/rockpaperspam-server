# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-06-22 11:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0018_auto_20170621_0819'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='is_bot',
            field=models.BooleanField(default=False),
        ),
    ]
