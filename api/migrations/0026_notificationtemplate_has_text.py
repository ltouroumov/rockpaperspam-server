# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-06-28 12:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0025_auto_20170628_1205'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificationtemplate',
            name='has_text',
            field=models.BooleanField(default=True),
        ),
    ]
