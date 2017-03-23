from api.models import Contact, Client
from django import template

register = template.Library()


@register.filter
def data(contact: Contact, tag):
    return str.join(", ", [item.value for item in contact.data_for_tag(tag)])


@register.filter
def last_sync(client: Client):
    return client.sync_set.order_by('-date').first().date
