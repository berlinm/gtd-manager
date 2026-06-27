import mistune
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(is_safe=True)
def markdown(value):
    """Render a Markdown string to safe HTML."""
    return mark_safe(mistune.html(value or ''))
