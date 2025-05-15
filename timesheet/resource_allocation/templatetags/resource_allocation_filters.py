# your_app/templatetags/resource_allocation_filters.py
from django import template
from itertools import groupby

register = template.Library()

@register.filter
def groupby_django(iterable, key):
    """
    Groups a list of objects by a dotted attribute key, like 'task.name'.
    Returns a list of (key, group) pairs where group is a list.
    """
    def resolve_attr(obj, key_path):
        for part in key_path.split('.'):
            obj = getattr(obj, part, None)
            if obj is None:
                break
        return obj

    sorted_iterable = sorted(iterable, key=lambda x: resolve_attr(x, key))
    grouped = groupby(sorted_iterable, key=lambda x: resolve_attr(x, key))
    return [(k, list(v)) for k, v in grouped]

@register.filter
def aggregate(items, field):
    """
    Sums the given field over all items.
    """
    try:
        return sum(getattr(item, field, 0) or 0 for item in items)
    except Exception:
        return 0
