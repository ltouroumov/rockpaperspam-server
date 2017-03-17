from django.contrib import admin
from .models import *


class ClientAdmin(admin.ModelAdmin):
    filter_horizontal = ('friends',)


class ContactAdmin(admin.ModelAdmin):
    filter_horizontal = ('numbers', 'emails')

# Register your models here.
admin.site.register(Client, ClientAdmin)
admin.site.register(Contact, ContactAdmin)
