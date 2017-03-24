from api.models import Contact, Client
from django import template

register = template.Library()


@register.filter
def data(contact, tags):
    return str.join(", ", [item.value for item in contact.data_for_tags(tags.split(','))])


@register.filter
def has_data(contact, tags):
    return contact.data_for_tags(tags.split(',')).count() > 0


@register.filter
def order_by(coll, columns):
    return coll.order_by(*columns.split(','))


@register.filter
def last_sync(client: Client):
    last = client.sync_set.order_by('-date').first()
    if last:
        return last.date
    else:
        return 'Never'
