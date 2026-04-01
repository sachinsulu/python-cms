from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def active_url(context, url):
    """
    Returns 'active' if the current request path matches the given URL,
    normalizing trailing slashes so '/rooms' == '/rooms/' both match.
    """
    request = context.get('request')
    if not request or not url:
        return ''
    current = request.path.rstrip('/')
    target = url.rstrip('/')
    if target and current == target:
        return 'active'
    return ''
