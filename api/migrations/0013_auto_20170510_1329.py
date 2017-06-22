# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-10 13:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_auto_20170428_1043'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='date_ended',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='game',
            name='date_started',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='move',
            name='move',
            field=models.CharField(choices=[('PAP', 'Paper'), ('SIS', 'Scissors'), ('ROC', 'Rock'), ('LIZ', 'Lizard'), ('SPO', 'Spock')], max_length=3),
        ),
    ]