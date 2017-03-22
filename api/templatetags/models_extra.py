from django import template

register = template.Library()


@register.filter
def data(contact, tag):
    return str.join(", ", [item.value for item in contact.data_for_tag(tag)])
