# core/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def split_title(value):
    """Return the part before the '|' character."""
    return value.split('|')[0].strip()
