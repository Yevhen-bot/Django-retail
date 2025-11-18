from django import template

register = template.Library()

@register.filter
def get_id(item):
    for key, value in item.items():
        if key.lower().endswith("id"):
            return value
    return None