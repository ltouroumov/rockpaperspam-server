from django.contrib import admin
from .models import *


class ContactAdmin(admin.ModelAdmin):
    filter_horizontal = ('numbers', 'emails')

# Register your models here.
admin.site.register(Client)
admin.site.register(Contact, ContactAdmin)
admin.site.register(PhoneNumber)
admin.site.register(EmailAddress)
