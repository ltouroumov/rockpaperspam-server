from django import template

register = template.Library()


@register.filter(name='times')
def times(number):
    return range(number)


@register.filter(name='times1')
def times1(number):
    return range(1, number+1)
