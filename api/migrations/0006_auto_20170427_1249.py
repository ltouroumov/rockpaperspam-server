# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-27 12:49
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_game_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.Contact'),
        ),
        migrations.AlterField(
            model_name='round',
            name='winner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.Player'),
        ),
    ]
