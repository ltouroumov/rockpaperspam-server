# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-08-05 16:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0031_notificationtemplate_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notificationtemplate',
            name='body_key',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='notificationtemplate',
            name='title_key',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]
