import datetime
from django import template
from django.template import Template, Context

register = template.Library()

@register.filter
def split(value, delimiter=','):
    if not value:
        return []
    return [v.strip() for v in value.split(delimiter)]

@register.filter
def replace_year(value):
    """
    Replaces {year} in a string with the current year.
    """
    if not isinstance(value, str):
        return value
    return value.replace('{year}', str(datetime.datetime.now().year))

@register.filter
def render_template(value):
    """
    Renders a string as a Django template.
    """
    if not isinstance(value, str):
        return value
    try:
        return Template(value).render(Context({}))
    except Exception:
        return value

@register.filter
def get_range(value):
    """
    Returns a range from 0 to value - 1. Safe to use in for loops.
    """
    try:
        return range(int(value))
    except (ValueError, TypeError):
        return []
