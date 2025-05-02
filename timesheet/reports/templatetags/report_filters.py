from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def unique_values(data, key):
    """
    Returns a list of unique values for a specific key from a list of dicts.
    """
    seen = set()
    unique_list = []
    for row in data:
        value = row.get(key)
        if value not in seen:
            seen.add(value)
            unique_list.append({'key': value})
    return unique_list