import datetime
from django import template

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




