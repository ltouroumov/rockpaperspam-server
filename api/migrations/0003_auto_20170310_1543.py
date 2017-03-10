# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2017-03-10 15:43
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20170310_1306'),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='EmailAddress',
            fields=[
                ('address', models.TextField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='PhoneNumber',
            fields=[
                ('number', models.TextField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.RenameField(
            model_name='contact',
            old_name='whatsapp',
            new_name='whatsapp_id',
        ),
        migrations.RemoveField(
            model_name='contact',
            name='contacts',
        ),
        migrations.RemoveField(
            model_name='contact',
            name='number',
        ),
        migrations.AddField(
            model_name='client',
            name='contact',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='api.Contact'),
        ),
        migrations.AddField(
            model_name='contact',
            name='emails',
            field=models.ManyToManyField(to='api.EmailAddress'),
        ),
        migrations.AddField(
            model_name='contact',
            name='numbers',
            field=models.ManyToManyField(to='api.PhoneNumber'),
        ),
    ]
