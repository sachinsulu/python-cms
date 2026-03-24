# media_manager/utils.py
from typing import Optional

from django.core.cache import cache

from .models import MediaFolder

FOLDER_TREE_CACHE_KEY = "media_folder_tree"
FOLDER_TREE_CACHE_TTL = 300  # 5 minutes


# ── Folder tree ───────────────────────────────────────────────────────────────

def _build_folder_tree_fast(nodes: list[dict], parent_id=None) -> list[dict]:
    """O(n) single-pass tree construction using an index."""
    index: dict = {}
    for node in nodes:
        pid = node["folder"].parent_id
        index.setdefault(pid, []).append(node)

    def attach_children(pid):
        children = index.get(pid, [])
        for child in children:
            child["children"] = attach_children(child["folder"].pk)
        return children

    return attach_children(parent_id)


def get_folder_tree(bust_cache: bool = False) -> list[dict]:
    """
    Load ALL folders in ONE query, build tree in Python (O(n)).
    Result is cached for FOLDER_TREE_CACHE_TTL seconds.
    """
    if not bust_cache:
        cached = cache.get(FOLDER_TREE_CACHE_KEY)
        if cached is not None:
            return cached

    all_folders = MediaFolder.objects.select_related("parent").order_by("name")
    flat = [{"folder": f, "children": []} for f in all_folders]
    tree = _build_folder_tree_fast(flat)
    cache.set(FOLDER_TREE_CACHE_KEY, tree, timeout=FOLDER_TREE_CACHE_TTL)
    return tree


def bust_folder_tree_cache():
    cache.delete(FOLDER_TREE_CACHE_KEY)


# ── Breadcrumbs ───────────────────────────────────────────────────────────────

def get_breadcrumbs(folder: Optional[MediaFolder]) -> list[MediaFolder]:
    """
    Walk up the parent chain for breadcrumb rendering.
    Worst case: O(depth), typically 3-5 levels max.
    Returns list from root → current folder.
    """
    if folder is None:
        return []
    crumbs = []
    node = folder
    while node is not None:
        crumbs.insert(0, node)
        node = node.parent
    return crumbs