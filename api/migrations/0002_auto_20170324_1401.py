# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-24 14:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='display_name',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='rawcontact',
            name='contact_name',
            field=models.CharField(blank=True, max_length=512),
        ),
    ]