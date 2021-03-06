# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-06-20 08:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_auto_20170619_1227'),
    ]

    operations = [
        migrations.CreateModel(
            name='Energy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('regen_rate', models.FloatField()),
                ('pool_size', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='EnergyLevel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('value', models.IntegerField()),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='levels', to='api.Energy')),
            ],
        ),
        migrations.AddField(
            model_name='client',
            name='energy',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.Energy'),
        ),
    ]
