from __future__ import unicode_literals

from django.db import models
from django.utils import timezone


class Endpoint(models.Model):
    name = models.CharField(max_length=1024)
    number = models.CharField(max_length=128)

    def __str__(self):
        return str.format("Endpoint({0.id}, {0.name}, {0.number})")
