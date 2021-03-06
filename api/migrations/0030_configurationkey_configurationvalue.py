# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-07-13 09:40
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0029_auto_20170628_1254'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConfigurationKey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=64)),
                ('value_type', models.CharField(choices=[('INT', 'Integer'), ('STR', 'String'), ('OBJ', 'Object (JSON)')], max_length=3)),
            ],
        ),
        migrations.CreateModel(
            name='ConfigurationValue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('value', models.TextField()),
                ('key', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='value_history', to='api.ConfigurationKey')),
            ],
        ),
    ]
