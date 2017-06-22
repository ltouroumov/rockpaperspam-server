# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-06-20 11:55
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0015_auto_20170620_0854'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='energy',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.Energy'),
        ),
        migrations.AlterField(
            model_name='move',
            name='move',
            field=models.CharField(choices=[('ROC', 'Rock'), ('PAP', 'Paper'), ('SPO', 'Spock'), ('SIS', 'Scissors'), ('LIZ', 'Lizard')], max_length=3),
        ),
    ]
