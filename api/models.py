from django.db import models
import uuid


class Client(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contact = models.OneToOneField(to='Contact')


class Contact(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=1024)
    whatsapp_id = models.CharField(max_length=512, default='0')
    numbers = models.ManyToManyField(to='PhoneNumber')
    emails = models.ManyToManyField(to='EmailAddress')

    def __str__(self):
        return str.format("Contact({0.id}, {0.name}, {0.whatsapp})", self)


class PhoneNumber(models.Model):
    # Canonical Phone Number (ex. +41793571289)
    number = models.CharField(max_length=1024, primary_key=True)


class EmailAddress(models.Model):
    address = models.CharField(max_length=1024, primary_key=True)
