from django.db import models
from datetime import datetime
import uuid


class Client(models.Model):
    id = models.UUIDField(primary_key=True)
    token = models.TextField(blank=True)
    profile = models.ForeignKey(to='Contact', blank=True)
    friends = models.ManyToManyField(to='Contact', related_name='friends')

    @property
    def friends_by_name(self):
        return self.friends.order_by('display_name')

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

    @property
    def key(self):
        return "%s/%d" % (self.contact_key, self.contact_id)

    @property
    def data(self):
        return Data.objects.filter(raw_contact__contact__id=self.id)

    def data_for_tags(self, tags):
        return Data.objects.filter(type__in=tags, raw_contact__contact__id=self.id)

    def __str__(self):
        return str.format("Contact({0.id}, {0.contact_id}/{0.contact_key}, {0.display_name})", self)


class RawContact(models.Model):
    contact = models.ForeignKey(to='Contact', related_name='raw_contacts')

    contact_type = models.CharField(max_length=256)
    contact_name = models.CharField(max_length=512, blank=True)

    def data_for_tags(self, tags):
        return self.data.filter(type__in=tags)

    def __str__(self):
        return str.format("RawContact({0.id}, {0.contact_type}, {0.contact_name})", self)


class Data(models.Model):
    TYPES = (
        ('NAME', 'Name'),
        ('PHONE', 'Phone Number'),
        ('EMAIL', 'Email Address'),
        ('WHATSAPP', 'Whatsapp ID'),
    )

    raw_contact = models.ForeignKey(to='RawContact', related_name='data')

    type = models.CharField(max_length=32, choices=TYPES)
    # Canonical Phone Number (ex. +41793571289)
    value = models.CharField(max_length=1024)

    def __str__(self):
        return self.value
