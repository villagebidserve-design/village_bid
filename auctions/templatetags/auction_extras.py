import re

from django import template
from django.utils.html import escape, mark_safe

register = template.Library()

@register.filter(is_safe=True)
def highlight(value, query):
    if not query or not value:
        return value

    text = escape(value)
    pattern = re.compile(re.escape(query), re.IGNORECASE)

    highlighted = pattern.sub(
        lambda match: f'<mark style="background: rgba(255, 193, 7, 0.35); padding: 0.1rem 0.2rem; border-radius: 0.2rem;">{match.group(0)}</mark>',
        text,
    )
    return mark_safe(highlighted)
