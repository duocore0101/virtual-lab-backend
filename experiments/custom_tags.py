from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    if dictionary and key:
        return dictionary.get(str(key)) or dictionary.get(key)
    return None