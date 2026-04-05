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
def split_phones(value):
    """
    Splits a string by multiple delimiters (comma, pipe, semicolon),
    normalizes each number (removes internal spaces, adds +977 if missing),
    and returns a list of formatted strings.
    """
    from core.phone_utils import split_and_normalize_phones
    return split_and_normalize_phones(value)

@register.filter
def clean_tel(value):
    """
    Removes all non-digit characters except '+' for valid tel: links.
    """
    if not value:
        return ""
    import re
    # Keep only digits and '+'
    return re.sub(r'[^\d+]', '', str(value))

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
@register.filter
def extract_src(value):
    """
    Extracts the 'src' attribute from an HTML tag string (e.g. <iframe>).
    If no src is found, returns the original value.
    """
    if not isinstance(value, str) or '<' not in value:
        return value
    import re
    match = re.search(r'src=["\']([^"\']+)["\']', value)
    if match:
        return match.group(1)
    return value


@register.filter
def split_read_more(value):
    """
    Splits content by the 'Read More' separator.
    Returns a dictionary with 'main' and 'extra' parts.
    """
    if not isinstance(value, str):
        return {'main': value, 'extra': None}
    
    separator = '<hr class="read-more-separator" style="border: 1px dashed #f60;" />'
    parts = value.split(separator)
    return {
        'main': parts[0],
        'extra': parts[1] if len(parts) > 1 else None
    }
