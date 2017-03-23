from django.db import models
from datetime import datetime
import uuid


class Client(models.Model):
    id = models.UUIDField(primary_key=True)
    token = models.TextField(blank=True)
    profile = models.ForeignKey(to='Contact', blank=True)
    friends = models.ManyToManyField(to='Contact', related_name='friends')

    def __str__(self):
        return str.format("Client({0.id}):{0.profile}", self)


class Sync(models.Model):
    client = models.ForeignKey(to='Client')
    date = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return "Sync({0.client_id}, {0.date})".format(self)


class Contact(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contact_id = models.BigIntegerField(default=0)
    contact_key = models.CharField(max_length=1024, default="0")
    display_name = models.CharField(max_length=1024)

    def data_for_tag(self, tag):
        return self.data.filter(type=tag)

    def __str__(self):
        return str.format("Contact({0.id}, {0.contact_id}/{0.contact_key}, {0.display_name})", self)


class Data(models.Model):
    TYPES = (
        ('NAME', 'Name'),
        ('PHONE', 'Phone Number'),
        ('EMAIL', 'Email Address'),
        ('WHATSAPP', 'Whatsapp ID'),
    )

    type = models.CharField(max_length=32, choices=TYPES)
    # Canonical Phone Number (ex. +41793571289)
    value = models.CharField(max_length=1024)

    contact = models.ForeignKey(to='Contact', related_name='data')

    def __str__(self):
        return self.value
