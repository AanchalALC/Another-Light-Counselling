# <your_app>/templatetags/text_extras.py
from django import template
from html import unescape

register = template.Library()

@register.filter
def html_unescape(value):
    """Decode HTML entities like &rsquo; into real characters, safely."""
    if value is None:
        return ""
    return unescape(str(value))
