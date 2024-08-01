
from django import template

register = template.Library()

@register.filter
def slice_from(value, start):
    """Returns a substring from 'start' to the end of the string."""
    try:
        return value[int(start):]
    except (ValueError, TypeError):
        return value
