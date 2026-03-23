# core/utils.py
from .models import Module, PageMeta
from .forms import PageMetaForm


def get_page_meta_context(url_name):
    """
    Returns the page_meta, page_meta_form, and module_url_name
    context dict for any list view that includes the page meta partial.
    """
    module = Module.objects.filter(url_name=url_name).first()
    page_meta = None
    if module:
        try:
            page_meta = module.page_meta
        except PageMeta.DoesNotExist:
            pass
    return {
        'page_meta':       page_meta,
        'page_meta_form':  PageMetaForm(instance=page_meta),
        'module_url_name': url_name,
    }