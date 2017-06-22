# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-06-22 12:57
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0019_auto_20170622_1126'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='creation_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='move',
            name='move',
            field=models.CharField(choices=[('ROC', 'Rock'), ('LIZ', 'Lizard'), ('SPO', 'Spock'), ('SIS', 'Scissors'), ('PAP', 'Paper')], max_length=3),
        ),
    ]