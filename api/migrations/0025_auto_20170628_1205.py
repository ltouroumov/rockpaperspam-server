# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-06-28 12:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0024_auto_20170628_1158'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='sent',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='move',
            name='move',
            field=models.CharField(choices=[('LIZ', 'Lizard'), ('ROC', 'Rock'), ('PAP', 'Paper'), ('SIS', 'Scissors'), ('SPO', 'Spock')], max_length=3),
        ),
    ]
