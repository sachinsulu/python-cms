from typing import Optional
from .models import MediaFolder


def build_folder_tree(
    nodes: list[dict],
    parent_id: Optional[int] = None,
) -> list[dict]:
    """
    Recursively build a tree from a flat list — zero extra DB queries.
    Each node: {"folder": MediaFolder, "children": [...]}
    """
    branch = []
    for node in nodes:
        if node["folder"].parent_id == parent_id:
            node["children"] = build_folder_tree(nodes, node["folder"].pk)
            branch.append(node)
    return branch


def get_folder_tree() -> list[dict]:
    """
    Load ALL folders in ONE query, build tree in Python.
    select_related('parent') covers parent name access without extra hits.
    """
    all_folders = MediaFolder.objects.select_related("parent").order_by("name")
    flat = [{"folder": f, "children": []} for f in all_folders]
    return build_folder_tree(flat, parent_id=None)


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