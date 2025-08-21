from django import template

register = template.Library()

@register.filter
def pluck(data, key):
    return [item[key] for item in data]
