# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-06-28 12:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0028_auto_20170628_1245'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notificationtemplate',
            name='id',
            field=models.SlugField(max_length=256, primary_key=True, serialize=False),
        ),
    ]