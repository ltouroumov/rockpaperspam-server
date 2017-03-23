from api.models import Contact, Client
from django import template

register = template.Library()


TYPE_MAPS = {
    'info': 'alert-info',
    'success': 'alert-success',
    'warning': 'alert-warning',
    'error': 'alert-danger'
}


@register.filter
def as_alert(tags):
    return TYPE_MAPS[tags] if tags in TYPE_MAPS else tags
