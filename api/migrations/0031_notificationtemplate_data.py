# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-08-05 16:10
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0030_configurationkey_configurationvalue'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificationtemplate',
            name='data',
            field=django.contrib.postgres.fields.jsonb.JSONField(default={}),
        ),
    ]
