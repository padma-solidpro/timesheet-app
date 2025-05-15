from django import template
register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, 0)

@register.filter
def get_allocation_hours(allocations, subtask_id):
    return sum([a.assigned_hours for a in allocations if a.subtask_id == subtask_id])

@register.filter
def get_remaining_hours(total, alloc):
    return total - alloc.assigned_hours
